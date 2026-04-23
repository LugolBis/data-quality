import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

def degrade_completeness(driver):
    """
    Completeness
    Degradation logic: Randomly delete 5% of the relationships between orders and products.
    This causes some order nodes to have no associated products (abnormal out-degree).
    """
    query = """
    MATCH (o:Order)-[r:ORDERS]->(p:Product)
    WITH r, rand() AS random
    WHERE random < 0.05
    DELETE r
    RETURN count(r) AS deleted_count
    """
    result = driver.execute_query(query, database_="neo4j")
    print(f"[-] Completeness degradation: Deleted {result.records[0]['deleted_count']} Order-Product relationships.")

def degrade_date_conformity(driver):
    """
    Conformity
    Degradation logic: Corrupt the format of 5% of the order dates from YYYY-MM-DD to DD/MM/YYYY.
    """
    query = """
    MATCH (o:Order)
    WHERE o.orderDate IS NOT NULL
    WITH o, rand() AS random
    WHERE random < 0.05
    SET o.orderDate = '04/07/1996' 
    RETURN count(o) AS modified_count
    """
    result = driver.execute_query(query, database_="neo4j")
    print(f"[-] Conformity degradation: Corrupted the date format of {result.records[0]['modified_count']} orders.")

def degrade_fd_consistency(driver):
    """
    Consistency
    Degradation logic: Break the dependency between Postal Code -> City. 
    Randomly modify the city of 5% of the customers without changing their postal code.
    """
    query = """
    MATCH (c:Customer)
    WHERE c.postalCode IS NOT NULL AND c.city IS NOT NULL
    WITH c, rand() AS random
    WHERE random < 0.05
    SET c.city = 'Invalid_City_FD'
    RETURN count(c) AS modified_count
    """
    result = driver.execute_query(query, database_="neo4j")
    print(f"[-] Consistency degradation: Created {result.records[0]['modified_count']} customer records with Functional Dependency (Postal Code -> City) conflicts.")

def degrade_schema_integrity(driver):
    """
    Integrity
    Degradation logic 1 (Missing value): Randomly remove the 'unitPrice' property from 5% of products.
    Degradation logic 2 (Type error): Change the 'unitsInStock' property from an integer to a string for 5% of products.
    """
    query_missing = """
    MATCH (p:Product)
    WITH p, rand() AS random
    WHERE random < 0.05
    REMOVE p.unitPrice
    RETURN count(p) AS modified_count
    """
    res1 = driver.execute_query(query_missing, database_="neo4j")
    
    query_type = """
    MATCH (p:Product)
    WHERE p.unitsInStock IS NOT NULL
    WITH p, rand() AS random
    WHERE random < 0.05
    SET p.unitsInStock = 'Out of stock'
    RETURN count(p) AS modified_count
    """
    res2 = driver.execute_query(query_type, database_="neo4j")
    print(f"[-] Schema validity degradation: Removed 'unitPrice' from {res1.records[0]['modified_count']} products, and changed 'unitsInStock' data type for {res2.records[0]['modified_count']} products.")

def degrade_uniqueness_duplicates(driver):
    """
    Uniqueness
    Degradation logic: Randomly clone 3 customer nodes to create exact duplicate nodes.
    """
    query = """
    MATCH (c:Customer)
    WITH c LIMIT 3
    CREATE (c_dup:Customer)
    SET c_dup = properties(c)
    RETURN count(c_dup) AS duplicated_count
    """
    result = driver.execute_query(query, database_="neo4j")
    print(f"[-] Uniqueness degradation: Forcefully cloned and created {result.records[0]['duplicated_count']} exact duplicate customer nodes.")

def run_all_degradations(driver):
    """
    Executes all data degradation functions in sequence.
    """
    print("Starting to inject dirty test data into the Northwind database...\n" + "-"*60)
    degrade_completeness(driver)
    degrade_date_conformity(driver)
    degrade_fd_consistency(driver)
    degrade_schema_integrity(driver)
    degrade_uniqueness_duplicates(driver)
    print("-" * 60 + "\nData degradation complete.")

if __name__ == "__main__":
    load_dotenv()

    NEO4J_URI = os.getenv("URI")
    NEO4J_USER = os.getenv("DB_USER")
    NEO4J_PASSWORD = os.getenv("DB_PW")
    DB_NAME = os.getenv("DB_NAME")

    db_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        run_all_degradations(db_driver)
    finally:
        db_driver.close()