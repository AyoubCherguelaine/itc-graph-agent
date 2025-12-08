from app.graph import graph_db

def seed_data():
    print("Seeding ITC BLIDA data into Neo4j...")
    try:
        graph_db.init_schema()
        
        # Clear existing data
        graph_db.query("MATCH (n) DETACH DELETE n")

        # Create Departments
        print("Creating Departments...")
        graph_db.query("""
        UNWIND ['Development', 'Design', 'Marketing', 'Content Creation', 'HR', 'Logistics'] AS dept
        CREATE (d:Department {name: dept})
        """)

        # Create Events
        print("Creating Events...")
        graph_db.query("""
        CREATE (e1:Event {name: 'ITC TALKS 6.0', date: '2025-04-08', description: 'Annual conference with tech leaders'})
        CREATE (e2:Event {name: 'ITCup', date: '2024-10-15', description: 'Technical competition'})
        CREATE (e3:Event {name: 'WelcomeDay', date: '2024-09-20', description: 'New members welcome event'})
        """)

        # Create Members and Relationships
        print("Creating Members...")
        graph_db.query("""
        CREATE (m1:Member {id: '1', name: 'Ayoub', role: 'President'})
        CREATE (m2:Member {id: '2', name: 'Sarah', role: 'Head of Design'})
        CREATE (m3:Member {id: '3', name: 'Karim', role: 'Head of Development'})
        CREATE (m4:Member {id: '4', name: 'Lina', role: 'Community Manager'})

        WITH m1, m2, m3, m4
        MATCH (dev:Department {name: 'Development'})
        MATCH (design:Department {name: 'Design'})
        MATCH (marketing:Department {name: 'Marketing'})
        MATCH (hr:Department {name: 'HR'})
        
        MATCH (italks:Event {name: 'ITC TALKS 6.0'})
        MATCH (itcup:Event {name: 'ITCup'})

        MERGE (m1)-[:MEMBER_OF]->(hr)
        MERGE (m2)-[:MEMBER_OF]->(design)
        MERGE (m3)-[:MEMBER_OF]->(dev)
        MERGE (m4)-[:MEMBER_OF]->(marketing)

        MERGE (m1)-[:ORGANIZES]->(italks)
        MERGE (m3)-[:ORGANIZES]->(itcup)
        MERGE (dev)-[:HOSTS]->(itcup)
        MERGE (marketing)-[:HOSTS]->(italks)
        """)
        
        print("Seeding complete!")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        graph_db.close()

if __name__ == "__main__":
    seed_data()
