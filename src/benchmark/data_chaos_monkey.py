import os

from dotenv import load_dotenv

from driver.neo4j_driver import Neo4jSession


def degrade_completeness(session: Neo4jSession, seed: int) -> None:
    """
    Completeness
    Degradation logic: Randomly delete 5% of the relationships between orders and
    products. This causes some order nodes to have no associated products
    (abnormal out-degree).
    """

    query = (
        "MATCH (o:Order)-[r:ORDERS]->(p:Product) "
        "WITH r, apoc.util.md5([toString(id(r)), toString($seed)]) AS hash "
        "WHERE substring(hash, 0, 4) < '0ccc' "
        "DELETE r "
        "RETURN count(r) AS deleted_count "
    )

    result = session.run_query(query, parameters={"seed": seed})
    record = result.single()

    if record:
        print(  # noqa: T201
            f"[-] Completeness degradation (Seed {seed}):",
            f" Deleted {record['deleted_count']} Order-Product relationships.",
        )


def degrade_date_conformity(session: Neo4jSession, seed: int) -> None:
    """
    Conformity
    Degradation logic: Corrupt the format of 5% of the order dates from YYYY-MM-DD to
    DD/MM/YYYY.
    """
    query = """
    MATCH (o:Order)
    WHERE o.orderDate IS NOT NULL
    WITH o, apoc.util.md5([toString(id(o)), toString($seed)]) AS hash
    WHERE substring(hash, 0, 4) < '0ccc'
    SET o.orderDate = '04/07/1996'
    RETURN count(o) AS modified_count
    """

    result = session.run_query(query, parameters={"seed": seed})
    record = result.single()

    if record:
        print(  # noqa: T201
            f"[-] Conformity degradation (Seed {seed}): Corrupted the date format of"
            f" {record['modified_count']} orders.",
        )


def degrade_fd_consistency(session: Neo4jSession, seed: int) -> None:
    """
    Consistency
    Degradation logic: Break the dependency between Postal Code -> City.
    Randomly modify the city of 5% of the customers without changing their postal code.
    """

    query = """
    MATCH (c:Customer)
    WHERE c.postalCode IS NOT NULL AND c.city IS NOT NULL
    WITH c, apoc.util.md5([toString(id(c)), toString($seed)]) AS hash
    WHERE substring(hash, 0, 4) < '0ccc'
    SET c.city = 'Invalid_City_FD'
    RETURN count(c) AS modified_count
    """

    result = session.run_query(query, parameters={"seed": seed})
    record = result.single()

    if record:
        print(  # noqa: T201
            f"[-] Consistency degradation (Seed {seed}):",
            f"Created {record['modified_count']} customer records with FD conflicts.",
        )


def degrade_schema_integrity(session: Neo4jSession, seed: int) -> None:
    """
    Integrity
    Degradation logic 1 (Missing value): Randomly remove the 'unitPrice' property from
    5% of products.
    Degradation logic 2 (Type error): Change the 'unitsInStock' property from an integer
     to a string for 5% of products.
    """
    query_missing = """
    MATCH (p:Product)
    WITH p, apoc.util.md5([toString(id(p)), toString($seed), "missing"]) AS hash
    WHERE substring(hash, 0, 4) < '0ccc'
    REMOVE p.unitPrice
    RETURN count(p) AS modified_count
    """
    res1 = session.run_query(query_missing, parameters={"seed": seed})
    record1 = res1.single()

    query_type = """
    MATCH (p:Product)
    WHERE p.unitsInStock IS NOT NULL
    WITH p, apoc.util.md5([toString(id(p)), toString($seed), "type"]) AS hash
    WHERE substring(hash, 0, 4) < '0ccc'
    SET p.unitsInStock = 'Out of stock'
    RETURN count(p) AS modified_count
    """
    res2 = session.run_query(query_type, parameters={"seed": seed})
    record2 = res2.single()

    if record1 and record2:
        print(  # noqa: T201
            f"[-] Schema validity degradation (Seed {seed}): Removed 'unitPrice' from",
            f" {record1['modified_count']} products, changed 'unitsInStock'",
            f" for {record2['modified_count']}.",
        )


def degrade_uniqueness_duplicates(session: Neo4jSession, seed: int) -> None:
    """
    Uniqueness
    Degradation logic: Randomly clone 3 customer nodes to create exact duplicate nodes.
    """

    query = """
    MATCH (c:Customer)
    WITH c
    ORDER BY apoc.util.md5([toString(id(c)), toString($seed)])
    LIMIT 3
    CREATE (c_dup:Customer)
    SET c_dup = properties(c)
    RETURN count(c_dup) AS duplicated_count
    """

    result = session.run_query(query, parameters={"seed": seed})
    record = result.single()

    if record:
        print(
            f"[-] Uniqueness degradation (Seed {seed}): Forcefully cloned",
            f" {record['duplicated_count']} duplicate customer nodes.",
        )


def degrade_label_accuracy(session: Neo4jSession, seed: int) -> None:
    """
    Accuracy/Validity
    Degradation logic: Query all existing label types. For each type, randomly select
    ~2% of the nodes, remove their original label, and assign a
    'Corrupted_<OriginalLabel>' label instead.
    """
    fetch_labels_query = """
    CALL db.labels() YIELD label
    RETURN label
    """
    labels_result = session.run_query(fetch_labels_query)
    labels: set[str] = {record["label"] for record in labels_result}

    if len(labels) < 2:  # noqa: PLR2004
        print(
            "[-] Label accuracy degradation: Not enough unique labels in the database"
            " to swap.",
        )
        return

    total_modified = 0

    for label in labels:
        other_labels = [l for l in labels if l != label]

        query = f"""
        MATCH (n:`{label}`)
        WITH n, apoc.util.md5([elementId(n), toString($seed), $label_str, "label_degrade"]) AS hash
        WHERE substring(hash, 0, 4) < '051e'
        WITH n, (apoc.text.charAt(hash, 4) + apoc.text.charAt(hash, 5)) % size($other_labels) AS random_idx
        WITH n, $other_labels[random_idx] AS wrong_label
        SET n:$([wrong_label])
        REMOVE n:$([$label_str])

        RETURN count(n) AS modified_count
        """

        result = session.run_query(
            query,  # ty:ignore[invalid-argument-type]
            parameters={
                "seed": seed,
                "label_str": label,
                "other_labels": other_labels,
            },
        )
        record = result.single()

        count = record["modified_count"] if record else 0
        if count > 0:
            print(
                f"[-] Label accuracy degradation (Seed {seed}): Changed {count} '{label}'"
                " nodes into other random existing labels.",
            )
            total_modified += count

    if total_modified > 0:
        print(
            f"    -> Total label corruptions: {total_modified} nodes assigned wrong labels.",
        )
    else:
        print(f"[-] Label accuracy degradation (Seed {seed}): No nodes modified.")


def run_all_degradations(session: Neo4jSession, seed: int = 42) -> None:
    """
    Executes all data degradation functions in sequence.
    """
    print(
        f"Starting to inject dirty test data into the database (Seed: {seed})...\n"
        + "-" * 60,
    )
    degrade_completeness(session, seed)
    degrade_date_conformity(session, seed)
    degrade_fd_consistency(session, seed)
    degrade_schema_integrity(session, seed)
    degrade_uniqueness_duplicates(session, seed)
    degrade_label_accuracy(session, seed)
    print("-" * 60 + "\nData degradation complete.")


def main() -> None:
    load_dotenv()

    neo4j_uri = os.getenv("URI")
    neo4j_user = os.getenv("DB_USER")
    neo4j_password = os.getenv("DB_PW")
    db_name = os.getenv("DB_NAME", "neo4j")

    global_seed = 42

    if neo4j_uri and neo4j_user and neo4j_password and db_name:
        with Neo4jSession(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
            database=db_name,
        ) as session:
            run_all_degradations(session, seed=global_seed)
    else:
        print("Error : the .env file isn't correctly configured.")


if __name__ == "__main__":
    main()
