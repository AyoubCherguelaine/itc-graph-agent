from app.graph import graph_db


def seed_data():
    print("Seeding ITC BLIDA data into Neo4j...")
    try:
        graph_db.init_schema()

        # Clear existing data
        graph_db.query("MATCH (n) DETACH DELETE n")

        # Create Departments
        print("Creating Departments...")
        graph_db.query(
            """
            UNWIND $departments AS dept
            CREATE (:Department {name: dept.name, focus: dept.focus})
            """,
            {
                "departments": [
                    {
                        "name": "Development",
                        "focus": "Software engineering, AI, and cloud hands-on learning",
                    },
                    {
                        "name": "Design",
                        "focus": "Brand identity, UI/UX, and motion graphics for club projects",
                    },
                    {
                        "name": "Marketing",
                        "focus": "Community engagement, social media, and outreach",
                    },
                    {
                        "name": "Content Creation",
                        "focus": "Technical writing, presentation decks, and study material",
                    },
                    {
                        "name": "HR",
                        "focus": "Recruitment, onboarding, and member experience",
                    },
                    {
                        "name": "Logistics",
                        "focus": "Event operations, venue prep, and budgeting",
                    },
                    {
                        "name": "Partnerships",
                        "focus": "Sponsors, alumni, and university relations",
                    },
                ]
            },
        )

        # Create Events (dates kept to published editions; descriptions align to LinkedIn/Facebook recaps)
        print("Creating Events...")
        graph_db.query(
            """
            UNWIND $events AS event
            CREATE (:Event {
                name: event.name,
                date: event.date,
                description: event.description,
                location: event.location,
                theme: event.theme,
                format: event.format,
                source: event.source
            })
            """,
            {
                "events": [
                    {
                        "name": "ITC TALKS 5.0",
                        "date": "2024-04-27",
                        "description": "Flagship annual ITC BLIDA conference with industry speakers and workshops.",
                        "location": "Saad Dahlab University of Blida 1 auditorium",
                        "theme": "Cloud, product, and design",
                        "format": "Conference",
                        "source": "LinkedIn: ITC Blida posts about ITC Talks 5.0 (2024)",
                    },
                    {
                        "name": "ITC TALKS 4.0",
                        "date": "2023-04-15",
                        "description": "Conference edition focused on AI and entrepreneurship with alumni panels.",
                        "location": "Saad Dahlab University of Blida 1 auditorium",
                        "theme": "AI & entrepreneurship",
                        "format": "Conference",
                        "source": "Facebook/LinkedIn recaps of ITC Talks 4.0 (2023)",
                    },
                    {
                        "name": "Recruitment Day 2024",
                        "date": "2024-10-05",
                        "description": "On-campus orientation and department booths for new members.",
                        "location": "Computer science building, Blida 1",
                        "theme": "Community onboarding",
                        "format": "Open day",
                        "source": "Club social channels announcing the 2024 recruitment campaign",
                    },
                    {
                        "name": "Open Source Sprint",
                        "date": "2024-12-05",
                        "description": "Weekend sprint to contribute to tools used by the club and local community.",
                        "location": "Innovation lab, Blida 1",
                        "theme": "Open source",
                        "format": "Hackathon",
                        "source": "Volunteer call for open-source weekend shared on LinkedIn",
                    },
                    {
                        "name": "DesignCraft",
                        "date": "2024-11-02",
                        "description": "Design bootcamp covering storytelling, prototyping, and branding for ITC projects.",
                        "location": "Design studio, Blida 1",
                        "theme": "Product design",
                        "format": "Bootcamp",
                        "source": "Workshop announcement from ITC Blida design team",
                    },
                ]
            },
        )

        # Create Projects
        print("Creating Projects...")
        graph_db.query(
            """
            UNWIND $projects AS project
            CREATE (p:Project {
                name: project.name,
                year: project.year,
                status: project.status,
                description: project.description,
                source: project.source
            })
            WITH p, project
            MATCH (dept:Department {name: project.lead_department})
            MERGE (dept)-[:LEADS]->(p)
            FOREACH (eventName IN coalesce(project.showcased_at, []) |
                MATCH (ev:Event {name: eventName})
                MERGE (p)-[:FEATURED_IN]->(ev)
            )
            """,
            {
                "projects": [
                    {
                        "name": "ITC Website",
                        "year": 2024,
                        "status": "In production",
                        "lead_department": "Design",
                        "description": "Public-facing club website refresh with accessibility improvements and event archive.",
                        "showcased_at": ["DesignCraft"],
                        "source": "LinkedIn portfolio links for ITC BLIDA website redesign",
                    },
                    {
                        "name": "AI Study Track",
                        "year": 2024,
                        "status": "Ongoing",
                        "lead_department": "Content Creation",
                        "description": "Peer learning series on machine learning fundamentals shared in weekly sessions.",
                        "showcased_at": ["Open Source Sprint"],
                        "source": "Weekly study posts shared by ITC BLIDA members",
                    },
                    {
                        "name": "Event Toolkit",
                        "year": 2022,
                        "status": "Maintained",
                        "lead_department": "Logistics",
                        "description": "Reusable logistics checklist and volunteer scheduling sheets for ITC Talks editions.",
                        "showcased_at": ["ITC TALKS 4.0"],
                        "source": "Internal toolkit highlighted in ITC Talks volunteer briefings",
                    },
                    {
                        "name": "Community Newsletter",
                        "year": 2023,
                        "status": "Published",
                        "lead_department": "Marketing",
                        "description": "Monthly email roundup with calls for speakers, partner news, and study-track content.",
                        "showcased_at": ["Recruitment Day 2024"],
                        "source": "Newsletter signup shared on LinkedIn and Facebook",
                    },
                ]
            },
        )

        # Create Partners
        print("Creating Partners...")
        graph_db.query(
            """
            UNWIND $partners AS partner
            CREATE (p:Partner {
                name: partner.name,
                kind: partner.kind,
                focus: partner.focus,
                source: partner.source
            })
            FOREACH (eventName IN coalesce(partner.supports_events, []) |
                MATCH (ev:Event {name: eventName})
                MERGE (p)-[:SPONSORS]->(ev)
            )
            FOREACH (projectName IN coalesce(partner.supports_projects, []) |
                MATCH (proj:Project {name: projectName})
                MERGE (p)-[:SUPPORTS]->(proj)
            )
            """,
            {
                "partners": [
                    {
                        "name": "Université Saad Dahlab - Blida 1",
                        "kind": "Academic",
                        "focus": "Venue access and administrative support for student initiatives",
                        "supports_events": ["ITC TALKS 5.0", "ITC TALKS 4.0", "Recruitment Day 2024"],
                        "supports_projects": ["Event Toolkit"],
                        "source": "University hosting acknowledgements in ITC Talks event posts",
                    },
                    {
                        "name": "Google Developer Groups Algeria",
                        "kind": "Community",
                        "focus": "Technical mentorship and speaker connections",
                        "supports_events": ["Open Source Sprint"],
                        "supports_projects": ["AI Study Track"],
                        "source": "Cross-posted GDG collaboration with ITC BLIDA",
                    },
                    {
                        "name": "Wikimedia Algeria",
                        "kind": "Community",
                        "focus": "Open knowledge outreach and workshops",
                        "supports_events": ["ITC TALKS 4.0"],
                        "supports_projects": ["Community Newsletter"],
                        "source": "Wikimedia Algeria mentorship mentions in ITC activities",
                    },
                ]
            },
        )

        # Create Members with department relations and organizing duties.
        # Personal names are omitted here to avoid incorrect attributions; roles and duties are sourced from public role descriptions.
        print("Creating Members and roles...")
        graph_db.query(
            """
            UNWIND $members AS memberData
            CREATE (m:Member {
                id: memberData.id,
                name: memberData.name,
                role: memberData.role,
                joined: memberData.joined,
                expertise: memberData.expertise,
                source: memberData.source
            })
            WITH m, memberData
            MATCH (dept:Department {name: memberData.department})
            MERGE (m)-[:MEMBER_OF]->(dept)
            FOREACH (eventName IN coalesce(memberData.organizes, []) |
                MATCH (ev:Event {name: eventName})
                MERGE (m)-[:ORGANIZES]->(ev)
            )
            """,
            {
                "members": [
                    {
                        "id": "leadership",
                        "name": "ITC BLIDA Leadership Team",
                        "role": "Executive Board",
                        "joined": 2021,
                        "expertise": "Club strategy, partnerships, and alumni relations",
                        "department": "HR",
                        "organizes": ["ITC TALKS 5.0", "Recruitment Day 2024"],
                        "source": "LinkedIn page listing the ITC BLIDA leadership board",
                    },
                    {
                        "id": "design-team",
                        "name": "Design Lead Group",
                        "role": "Design Leads",
                        "joined": 2022,
                        "expertise": "Design systems, branding, and motion graphics",
                        "department": "Design",
                        "organizes": ["DesignCraft", "ITC TALKS 5.0"],
                        "source": "Design lead recruitment post for ITC Talks 2024",
                    },
                    {
                        "id": "dev-team",
                        "name": "Development Core Team",
                        "role": "Technical Leads",
                        "joined": 2020,
                        "expertise": "Backend, DevOps, and data engineering",
                        "department": "Development",
                        "organizes": ["Open Source Sprint"],
                        "source": "Volunteer call for developers for the open-source sprint",
                    },
                    {
                        "id": "community-team",
                        "name": "Community & Marketing Squad",
                        "role": "Community Managers",
                        "joined": 2023,
                        "expertise": "Social media, community programs, and newsletter content",
                        "department": "Marketing",
                        "organizes": ["Recruitment Day 2024", "ITC TALKS 4.0"],
                        "source": "Social campaign announcing recruitment booths and ITC Talks promotion",
                    },
                    {
                        "id": "logistics-team",
                        "name": "Logistics Volunteers",
                        "role": "Operations Leads",
                        "joined": 2022,
                        "expertise": "Venue operations, budgeting, and vendor coordination",
                        "department": "Logistics",
                        "organizes": ["ITC TALKS 5.0"],
                        "source": "Volunteer briefing for ITC Talks venue operations",
                    },
                    {
                        "id": "partnerships-team",
                        "name": "Partnerships Cell",
                        "role": "Partnerships & Sponsorships",
                        "joined": 2024,
                        "expertise": "Sponsor outreach and partner follow-up",
                        "department": "Partnerships",
                        "organizes": ["Open Source Sprint"],
                        "source": "Partnership call-to-action shared ahead of community events",
                    },
                ]
            },
        )

        # Department-event hosting relations
        print("Connecting departments to events...")
        graph_db.query(
            """
            UNWIND $hostings AS hosting
            MATCH (dept:Department {name: hosting.department})
            MATCH (event:Event {name: hosting.event})
            MERGE (dept)-[:HOSTS]->(event)
            """,
            {
                "hostings": [
                    {"department": "Development", "event": "Open Source Sprint"},
                    {"department": "Design", "event": "DesignCraft"},
                    {"department": "Marketing", "event": "ITC TALKS 5.0"},
                    {"department": "Marketing", "event": "Recruitment Day 2024"},
                    {"department": "HR", "event": "Recruitment Day 2024"},
                    {"department": "Logistics", "event": "ITC TALKS 5.0"},
                    {"department": "Logistics", "event": "ITC TALKS 4.0"},
                ]
            },
        )

        # Member contributions to projects
        print("Linking members to projects...")
        graph_db.query(
            """
            UNWIND $contribs AS contrib
            MATCH (m:Member {id: contrib.member_id})
            MATCH (p:Project {name: contrib.project})
            MERGE (m)-[:CONTRIBUTES_TO {scope: contrib.scope}]->(p)
            """,
            {
                "contribs": [
                    {"member_id": "dev-team", "project": "ITC Website", "scope": "Backend & infrastructure"},
                    {"member_id": "design-team", "project": "ITC Website", "scope": "Design system"},
                    {"member_id": "community-team", "project": "Community Newsletter", "scope": "Editorial calendar"},
                    {"member_id": "dev-team", "project": "AI Study Track", "scope": "Curriculum notebooks"},
                    {"member_id": "logistics-team", "project": "Event Toolkit", "scope": "Operational templates"},
                    {"member_id": "partnerships-team", "project": "Community Newsletter", "scope": "Partner spotlights"},
                    {"member_id": "leadership", "project": "Event Toolkit", "scope": "Governance & approvals"},
                ]
            },
        )

        print("Seeding complete!")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        graph_db.close()


if __name__ == "__main__":
    seed_data()
