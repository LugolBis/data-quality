import os
from dotenv import load_dotenv
from driver.neo4j_driver import Neo4jSession

def degrade_completeness(session, seed: int):
    """
    Completeness
    Degradation logic: Randomly delete 5% of the relationships between orders and products.
    This causes some order nodes to have no associated products (abnormal out-degree).
    """
    query = """
    MATCH (o:Order)-[r:ORDERS]->(p:Product)
    WITH r, apoc.util.md5([toString(id(r)), toString($seed)]) AS hash
    WHERE substring(hash, 0, 4) < '0ccc' 
    DELETE r
    RETURN count(r) AS deleted_count
    """
    result = session.run_query(query, parameters={"seed": seed})
    record = result.single()
    print(f"[-] Completeness degradation (Seed {seed}): Deleted {record['deleted_count']} Order-Product relationships.")

def degrade_date_conformity(session, seed: int):
    """
    Conformity
    Degradation logic: Corrupt the format of 5% of the order dates from YYYY-MM-DD to DD/MM/YYYY.
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
    print(f"[-] Conformity degradation (Seed {seed}): Corrupted the date format of {record['modified_count']} orders.")

def degrade_fd_consistency(session, seed: int):
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
    print(f"[-] Consistency degradation (Seed {seed}): Created {record['modified_count']} customer records with FD conflicts.")

def degrade_schema_integrity(session, seed: int):
    """
    Integrity
    Degradation logic 1 (Missing value): Randomly remove the 'unitPrice' property from 5% of products.
    Degradation logic 2 (Type error): Change the 'unitsInStock' property from an integer to a string for 5% of products.
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
    
    print(f"[-] Schema validity degradation (Seed {seed}): Removed 'unitPrice' from {record1['modified_count']} products, changed 'unitsInStock' for {record2['modified_count']}.")

def degrade_uniqueness_duplicates(session, seed: int):
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
    print(f"[-] Uniqueness degradation (Seed {seed}): Forcefully cloned {record['duplicated_count']} duplicate customer nodes.")

def degrade_label_accuracy(session, seed: int):
    """
    Accuracy/Validity
    Degradation logic: Query all existing label types. For each type, randomly select ~2% of the nodes,
    remove their original label, and assign a 'Corrupted_<OriginalLabel>' label instead.
    """
    fetch_labels_query = """
    CALL db.labels() YIELD label 
    WHERE NOT label STARTS WITH 'Corrupted_' 
    RETURN label
    """
    labels_result = session.run_query(fetch_labels_query)
    labels = [record["label"] for record in labels_result]
    
    total_modified = 0
    
    for label in labels:
        query = f"""
        MATCH (n:`{label}`)
        WITH n, apoc.util.md5([toString(id(n)), toString($seed), $label_str, "label_degrade"]) AS hash
        WHERE substring(hash, 0, 4) < '051e'
        WITH n
        CALL apoc.create.addLabels(n, ['Corrupted_' + $label_str]) YIELD node
        CALL apoc.create.removeLabels(node, [$label_str]) YIELD node AS finalNode
        RETURN count(finalNode) AS modified_count
        """
        
        result = session.run_query(query, parameters={"seed": seed, "label_str": label})
        record = result.single()
        
        count = record["modified_count"] if record else 0
        if count > 0:
            print(f"[-] Label accuracy degradation (Seed {seed}): Changed {count} '{label}' nodes to 'Corrupted_{label}'.")
            total_modified += count
            
    if total_modified > 0:
        print(f"    -> Total label corruptions: {total_modified} nodes affected.")
    else:
        print(f"[-] Label accuracy degradation (Seed {seed}): No nodes modified (dataset might be too small for a 2% hit rate).")

def run_all_degradations(session, seed: int = 42):
    """
    Executes all data degradation functions in sequence.
    """
    print(f"Starting to inject dirty test data into the database (Seed: {seed})...\n" + "-"*60)
    degrade_completeness(session, seed)
    degrade_date_conformity(session, seed)
    degrade_fd_consistency(session, seed)
    degrade_schema_integrity(session, seed)
    degrade_uniqueness_duplicates(session, seed)
    degrade_label_accuracy(session, seed)
    print("-" * 60 + "\nData degradation complete.")

if __name__ == "__main__":
    load_dotenv()

    NEO4J_URI = os.getenv("URI")
    NEO4J_USER = os.getenv("DB_USER")
    NEO4J_PASSWORD = os.getenv("DB_PW")
    DB_NAME = os.getenv("DB_NAME", "neo4j")
    
    GLOBAL_SEED = 42 

    with Neo4jSession(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD, database=DB_NAME) as session:
        run_all_degradations(session, seed=GLOBAL_SEED)