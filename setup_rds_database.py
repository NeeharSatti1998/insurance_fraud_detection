import mysql.connector
from mysql.connector import Error

def create_table():
    try:
        conn = mysql.connector.connect(
            host='insurance-fraud-db.cobaiu8aw8xi.us-east-1.rds.amazonaws.com',
            user='admin',
            password='NeeharSatti1998',
            database='insurance_fraud_db'
        )
        if conn.is_connected():
            print("Connected to RDS successfully!")
            cursor = conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age INT,
                policy_state VARCHAR(10),
                policy_csl VARCHAR(20),
                policy_deductable INT,
                umbrella_limit INT,
                insured_sex VARCHAR(10),
                insured_education_level VARCHAR(50),
                insured_occupation VARCHAR(100),
                insured_hobbies VARCHAR(100),
                insured_relationship VARCHAR(50),
                incident_type VARCHAR(100),
                collision_type VARCHAR(50),
                incident_severity VARCHAR(50),
                authorities_contacted VARCHAR(50),
                incident_state VARCHAR(10),
                incident_city VARCHAR(50),
                number_of_vehicles_involved INT,
                bodily_injuries INT,
                witnesses INT,
                police_report_available VARCHAR(20),
                total_claim_amount FLOAT,
                auto_make VARCHAR(50),
                auto_model VARCHAR(50),
                auto_year INT,
                claim_ratio_bin VARCHAR(20),
                prediction VARCHAR(10),
                probability FLOAT
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("Table created successfully.")
        else:
            print("Failed to connect.")
    except Error as e:
        print("Error:", e)
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    create_table()
