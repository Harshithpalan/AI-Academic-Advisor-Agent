"""Course catalog and degree requirements for the academic advisor engine.

Catalog models a BS Computer Science degree. Categories:
  core      - required CS core sequence
  math      - required math
  science   - required lab sciences (pick a sequence)
  breadth   - humanities/social-science electives
  elective  - CS/technical electives
  capstone  - senior capstone
"""

GRADE_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
}
PASSING = {"A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D"}

# code, title, credits, prerequisites, terms offered, category, blurb
COURSES = [
    # ---- CS core ----
    ("CS111", "Introduction to Programming", 4, [], ["fall", "spring", "summer"], "core",
     "Python fundamentals: control flow, functions, data structures."),
    ("CS112", "Object-Oriented Programming", 4, ["CS111"], ["fall", "spring", "summer"], "core",
     "Java, OOP design, testing, basic algorithms."),
    ("CS210", "Data Structures", 4, ["CS112"], ["fall", "spring", "summer"], "core",
     "Lists, trees, hash tables, heaps, complexity analysis."),
    ("CS220", "Computer Systems I", 4, ["CS112"], ["fall", "spring"], "core",
     "C programming, memory, machine-level representation."),
    ("CS230", "Discrete Mathematics", 3, ["CS111", "MATH151"], ["fall", "spring"], "core",
     "Logic, proofs, sets, graphs, counting — foundation for theory."),
    ("CS310", "Algorithms", 4, ["CS210", "CS230"], ["fall", "spring"], "core",
     "Sorting, graph algorithms, dynamic programming, NP-completeness."),
    ("CS320", "Computer Systems II", 4, ["CS220"], ["fall", "spring"], "core",
     "Processes, virtual memory, concurrency basics."),
    ("CS330", "Databases", 3, ["CS210"], ["fall", "spring"], "core",
     "Relational model, SQL, transactions, indexing."),
    ("CS340", "Computer Networks", 3, ["CS320"], ["fall", "spring"], "core",
     "TCP/IP stack, routing, sockets programming."),
    ("CS350", "Operating Systems", 4, ["CS320", "CS310"], ["fall", "spring"], "core",
     "Scheduling, synchronization, file systems, virtual memory."),
    ("CS360", "Software Engineering", 3, ["CS310"], ["fall", "spring"], "core",
     "Agile, design patterns, version control, team project."),
    ("CS370", "Theory of Computation", 3, ["CS310"], ["spring"], "core",
     "Automata, formal languages, Turing machines, decidability."),
    ("CS490", "Senior Capstone Project", 4, ["CS360"], ["fall", "spring"], "capstone",
     "Two-semester team project with industry or research sponsor."),

    # ---- Math ----
    ("MATH151", "Calculus I", 4, [], ["fall", "spring", "summer"], "math",
     "Limits, derivatives, integrals."),
    ("MATH152", "Calculus II", 4, ["MATH151"], ["fall", "spring", "summer"], "math",
     "Series, integration techniques, multivariable intro."),
    ("MATH210", "Linear Algebra", 3, ["MATH151"], ["fall", "spring"], "math",
     "Vectors, matrices, eigenvalues — key for ML and graphics."),
    ("MATH230", "Probability & Statistics", 3, ["MATH152"], ["fall", "spring"], "math",
     "Distributions, inference, regression — key for data science."),

    # ---- Science (pick one sequence) ----
    ("PHYS151", "Physics I (Mechanics)", 4, ["MATH151"], ["fall", "spring"], "science",
     "Newtonian mechanics with calculus."),
    ("PHYS152", "Physics II (E&M)", 4, ["PHYS151"], ["fall", "spring"], "science",
     "Electricity, magnetism, circuits."),
    ("CHEM101", "General Chemistry I", 4, [], ["fall", "spring"], "science",
     "Atoms, bonding, stoichiometry."),
    ("CHEM102", "General Chemistry II", 4, ["CHEM101"], ["spring"], "science",
     "Thermodynamics, kinetics, equilibrium."),
    ("BIO101", "Biology I", 4, [], ["fall", "spring"], "science",
     "Cell biology and genetics."),
    ("BIO102", "Biology II", 4, ["BIO101"], ["spring"], "science",
     "Organismal biology, ecology, evolution."),

    # ---- CS electives ----
    ("CS410", "Machine Learning", 3, ["CS310", "MATH210", "MATH230"], ["fall"], "elective",
     "Supervised/unsupervised learning, neural nets, model evaluation."),
    ("CS411", "Deep Learning", 3, ["CS410"], ["spring"], "elective",
     "CNNs, transformers, training at scale."),
    ("CS420", "Computer Graphics", 3, ["CS310", "MATH210"], ["spring"], "elective",
     "Rendering, shaders, 3D geometry."),
    ("CS430", "Cybersecurity", 3, ["CS340"], ["fall"], "elective",
     "Threat models, crypto basics, web and network security."),
    ("CS440", "Distributed Systems", 3, ["CS350"], ["spring"], "elective",
     "Consensus, replication, cloud-scale architectures."),
    ("CS450", "Compilers", 3, ["CS370"], ["fall"], "elective",
     "Lexing, parsing, optimization, code generation."),
    ("CS460", "Human-Computer Interaction", 3, ["CS310"], ["spring"], "elective",
     "Usability, prototyping, user studies."),
    ("CS470", "Data Science", 3, ["CS330", "MATH230"], ["fall"], "elective",
     "Pipelines, visualization, applied statistics."),
    ("CS480", "Mobile App Development", 3, ["CS310"], ["spring"], "elective",
     "iOS/Android, mobile UI patterns, app publishing."),
    ("CS485", "Cloud Computing", 3, ["CS350"], ["fall"], "elective",
     "Containers, serverless, IaC, cost/performance tradeoffs."),
    ("CS495", "AI & Natural Language", 3, ["CS410"], ["spring"], "elective",
     "Language models, embeddings, RAG, evaluation."),

    # ---- Breadth electives ----
    ("ENG210", "Technical Writing", 3, [], ["fall", "spring"], "breadth",
     "Writing for engineers: docs, proposals, reports."),
    ("PHIL220", "Ethics in Technology", 3, [], ["fall", "spring"], "breadth",
     "Privacy, bias, professional responsibility."),
    ("ECON101", "Microeconomics", 3, [], ["fall", "spring"], "breadth",
     "Markets, incentives, game theory intro."),
    ("PSYCH101", "Intro to Psychology", 3, [], ["fall", "spring"], "breadth",
     "Cognition, behavior, research methods."),
    ("COMM201", "Public Speaking", 3, [], ["fall", "spring"], "breadth",
     "Presentation skills for technical audiences."),
    ("HIST240", "History of Computing", 3, [], ["spring"], "breadth",
     "From Babbage to the internet age."),
]

CATALOG = {
    c[0]: {
        "code": c[0], "title": c[1], "credits": c[2], "prereqs": c[3],
        "terms": c[4], "category": c[5], "blurb": c[6],
    } for c in COURSES
}

# Degree requirements for BS Computer Science (120 credits)
DEGREE = {
    "name": "BS Computer Science",
    "total_credits": 120,
    "requirements": [
        {"category": "core", "label": "CS Core", "credits": 46,
         "required": ["CS111", "CS112", "CS210", "CS220", "CS230", "CS310",
                      "CS320", "CS330", "CS340", "CS350", "CS360", "CS370"]},
        {"category": "capstone", "label": "Capstone", "credits": 4,
         "required": ["CS490"]},
        {"category": "math", "label": "Mathematics", "credits": 14,
         "required": ["MATH151", "MATH152", "MATH210", "MATH230"]},
        {"category": "science", "label": "Science (one sequence)", "credits": 8,
         "choose_credits": 8,
         "sequences": [["PHYS151", "PHYS152"], ["CHEM101", "CHEM102"],
                      ["BIO101", "BIO102"]]},
        {"category": "elective", "label": "CS Electives", "credits": 12,
         "choose_credits": 12},
        {"category": "breadth", "label": "Breadth Electives", "credits": 12,
         "choose_credits": 12},
        # remainder = free credits from any category to reach 120
    ],
}
