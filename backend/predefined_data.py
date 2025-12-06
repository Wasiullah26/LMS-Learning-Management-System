"""
Predefined data for LMS system
Contains admin credentials, specializations, and courses
"""

# Admin Configuration
ADMIN_CONFIG = {
    'email': 'admin-moodle@ncirl.ie',
    'password': 'admin-moodle@1',
    'name': 'System Administrator',
    'role': 'admin'
}

# Specializations Data
SPECIALIZATIONS_DATA = [
    {
        'name': 'MSc in Data Analytics',
        'code': 'MSC-DA',
        'description': 'Master of Science in Data Analytics - Learn advanced data analysis techniques, machine learning, and big data processing.'
    },
    {
        'name': 'MSc in Cyber Security',
        'code': 'MSC-CS',
        'description': 'Master of Science in Cyber Security - Master network security, cryptography, ethical hacking, and security risk management.'
    },
    {
        'name': 'MSc in Cloud Computing',
        'code': 'MSC-CC',
        'description': 'Master of Science in Cloud Computing - Design and deploy scalable cloud architectures, DevOps practices, and cloud services.'
    },
    {
        'name': 'MSc in Software Engineering',
        'code': 'MSC-SE',
        'description': 'Master of Science in Software Engineering - Learn software design patterns, agile methodologies, testing, and project management.'
    },
    {
        'name': 'MSc in Artificial Intelligence',
        'code': 'MSC-AI',
        'description': 'Master of Science in Artificial Intelligence - Explore machine learning, deep learning, NLP, and computer vision.'
    },
    {
        'name': 'MSc in DevOps',
        'code': 'MSC-DO',
        'description': 'Master of Science in DevOps - Master containerization, CI/CD pipelines, infrastructure as code, and monitoring.'
    },
    {
        'name': 'MSc in Blockchain Technology',
        'code': 'MSC-BT',
        'description': 'Master of Science in Blockchain Technology - Learn blockchain concepts, smart contracts, cryptocurrency, and consensus mechanisms.'
    },
    {
        'name': 'MSc in Digital Transformation',
        'code': 'MSC-DT',
        'description': 'Master of Science in Digital Transformation - Understand digital strategy, business models, change management, and emerging technologies.'
    }
]

# Courses Data organized by specialization code
COURSES_BY_SPECIALIZATION = {
    'MSC-DA': [
        {
            'title': 'Data Mining and Machine Learning',
            'description': 'Explore data mining techniques and machine learning algorithms for extracting insights from large datasets. Learn supervised and unsupervised learning, feature engineering, and model evaluation.',
            'instructor_name': 'Dr. Sarah Johnson',
            'instructor_email': 'sarah.johnson@ncirl.ie'
        },
        {
            'title': 'Big Data Analytics',
            'description': 'Learn to process and analyze big data using distributed computing frameworks and tools. Master Hadoop, Spark, and cloud-based analytics platforms.',
            'instructor_name': 'Dr. Michael Chen',
            'instructor_email': 'michael.chen@ncirl.ie'
        },
        {
            'title': 'Statistical Analysis and Visualization',
            'description': 'Master statistical methods and data visualization techniques for effective data communication. Learn R, Python visualization libraries, and dashboard creation.',
            'instructor_name': 'Dr. Emily Rodriguez',
            'instructor_email': 'emily.rodriguez@ncirl.ie'
        },
        {
            'title': 'Business Intelligence and Data Warehousing',
            'description': 'Design and implement data warehouses and business intelligence solutions for organizations. Learn ETL processes, OLAP, and BI tools.',
            'instructor_name': 'Dr. David Thompson',
            'instructor_email': 'david.thompson@ncirl.ie'
        }
    ],
    'MSC-CS': [
        {
            'title': 'Network Security',
            'description': 'Learn to secure network infrastructure, detect threats, and implement security protocols. Master firewalls, intrusion detection systems, and network monitoring.',
            'instructor_name': 'Dr. James Wilson',
            'instructor_email': 'james.wilson@ncirl.ie'
        },
        {
            'title': 'Cryptography and Secure Communications',
            'description': 'Study cryptographic algorithms, protocols, and secure communication systems. Learn symmetric and asymmetric encryption, digital signatures, and key management.',
            'instructor_name': 'Dr. Lisa Anderson',
            'instructor_email': 'lisa.anderson@ncirl.ie'
        },
        {
            'title': 'Ethical Hacking and Penetration Testing',
            'description': 'Learn ethical hacking techniques and penetration testing methodologies. Master vulnerability assessment, exploit development, and security auditing.',
            'instructor_name': 'Dr. Robert Martinez',
            'instructor_email': 'robert.martinez@ncirl.ie'
        },
        {
            'title': 'Security Risk Management',
            'description': 'Understand security risk assessment, management frameworks, and compliance requirements. Learn ISO 27001, NIST, and risk mitigation strategies.',
            'instructor_name': 'Dr. Jennifer Lee',
            'instructor_email': 'jennifer.lee@ncirl.ie'
        }
    ],
    'MSC-CC': [
        {
            'title': 'Cloud Platform Programming',
            'description': 'Learn cloud platform programming concepts, services, and best practices for building scalable applications on cloud platforms. Master AWS, Azure, and GCP SDKs.',
            'instructor_name': 'Adriana Chis',
            'instructor_email': 'adriana.chis@ncirl.ie'
        },
        {
            'title': 'Cloud DevOpsSec',
            'description': 'Comprehensive course covering DevOps practices, CI/CD pipelines, security in cloud environments, and automation tools. Learn Terraform, Ansible, and security best practices.',
            'instructor_name': 'Vikas Sahni',
            'instructor_email': 'vikas.sahni@ncirl.ie'
        },
        {
            'title': 'Cloud Architecture',
            'description': 'Design and implement scalable, resilient cloud architectures. Learn about microservices, serverless, and cloud design patterns. Master high availability and disaster recovery.',
            'instructor_name': 'J. Hennessy',
            'instructor_email': 'j.hennessy@ncirl.ie'
        },
        {
            'title': 'Cloud Infrastructure and Services',
            'description': 'Master cloud infrastructure management, service models, and deployment strategies. Learn IaaS, PaaS, SaaS, and hybrid cloud solutions.',
            'instructor_name': 'Dr. Mark Brown',
            'instructor_email': 'mark.brown@ncirl.ie'
        }
    ],
    'MSC-SE': [
        {
            'title': 'Software Design Patterns',
            'description': 'Learn design patterns and architectural principles for building maintainable software systems. Master creational, structural, and behavioral patterns.',
            'instructor_name': 'Dr. Patricia White',
            'instructor_email': 'patricia.white@ncirl.ie'
        },
        {
            'title': 'Agile Software Development',
            'description': 'Master agile methodologies, Scrum, Kanban, and collaborative software development practices. Learn sprint planning, retrospectives, and team collaboration.',
            'instructor_name': 'Dr. Kevin Davis',
            'instructor_email': 'kevin.davis@ncirl.ie'
        },
        {
            'title': 'Software Testing and Quality Assurance',
            'description': 'Learn testing strategies, automation, and quality assurance processes for software development. Master unit testing, integration testing, and test-driven development.',
            'instructor_name': 'Dr. Amanda Taylor',
            'instructor_email': 'amanda.taylor@ncirl.ie'
        },
        {
            'title': 'Software Project Management',
            'description': 'Understand project management principles, planning, and execution in software development contexts. Learn PMBOK, estimation techniques, and team leadership.',
            'instructor_name': 'Dr. Christopher Moore',
            'instructor_email': 'christopher.moore@ncirl.ie'
        }
    ],
    'MSC-AI': [
        {
            'title': 'Machine Learning Fundamentals',
            'description': 'Introduction to machine learning algorithms, supervised and unsupervised learning techniques. Learn regression, classification, clustering, and model evaluation.',
            'instructor_name': 'Dr. Rachel Green',
            'instructor_email': 'rachel.green@ncirl.ie'
        },
        {
            'title': 'Deep Learning and Neural Networks',
            'description': 'Explore deep learning architectures, neural networks, and advanced AI models. Master CNNs, RNNs, transformers, and transfer learning.',
            'instructor_name': 'Dr. Thomas Harris',
            'instructor_email': 'thomas.harris@ncirl.ie'
        },
        {
            'title': 'Natural Language Processing',
            'description': 'Learn to process and understand human language using AI and machine learning techniques. Master text preprocessing, sentiment analysis, and language models.',
            'instructor_name': 'Dr. Nicole Clark',
            'instructor_email': 'nicole.clark@ncirl.ie'
        },
        {
            'title': 'Computer Vision',
            'description': 'Study image processing, object recognition, and computer vision applications. Learn image classification, object detection, and image segmentation.',
            'instructor_name': 'Dr. Steven Lewis',
            'instructor_email': 'steven.lewis@ncirl.ie'
        }
    ],
    'MSC-DO': [
        {
            'title': 'Containerization and Orchestration',
            'description': 'Master Docker, Kubernetes, and container orchestration technologies. Learn container networking, storage, and scaling strategies.',
            'instructor_name': 'Dr. Michelle Adams',
            'instructor_email': 'michelle.adams@ncirl.ie'
        },
        {
            'title': 'CI/CD Pipeline Development',
            'description': 'Build and optimize continuous integration and deployment pipelines. Master Jenkins, GitLab CI, GitHub Actions, and pipeline automation.',
            'instructor_name': 'Dr. Brian Scott',
            'instructor_email': 'brian.scott@ncirl.ie'
        },
        {
            'title': 'Infrastructure as Code',
            'description': 'Learn to manage infrastructure using code with Terraform, Ansible, and similar tools. Master declarative infrastructure and configuration management.',
            'instructor_name': 'Dr. Kimberly Young',
            'instructor_email': 'kimberly.young@ncirl.ie'
        },
        {
            'title': 'Monitoring and Observability',
            'description': 'Implement monitoring, logging, and observability solutions for DevOps environments. Learn Prometheus, Grafana, ELK stack, and distributed tracing.',
            'instructor_name': 'Dr. Daniel King',
            'instructor_email': 'daniel.king@ncirl.ie'
        }
    ],
    'MSC-BT': [
        {
            'title': 'Blockchain Concepts',
            'description': 'Introduction to blockchain technology, distributed ledgers, smart contracts, and cryptocurrency fundamentals. Learn Bitcoin, Ethereum, and blockchain architecture.',
            'instructor_name': 'Sean Heeney',
            'instructor_email': 'sean.heeney@ncirl.ie'
        },
        {
            'title': 'Smart Contract Development',
            'description': 'Learn to develop, test, and deploy smart contracts on blockchain platforms. Master Solidity, testing frameworks, and security best practices.',
            'instructor_name': 'Dr. Laura Turner',
            'instructor_email': 'laura.turner@ncirl.ie'
        },
        {
            'title': 'Cryptocurrency and Digital Assets',
            'description': 'Understand cryptocurrency systems, digital asset management, and blockchain economics. Learn tokenomics, DeFi, and digital wallet security.',
            'instructor_name': 'Dr. Ryan Phillips',
            'instructor_email': 'ryan.phillips@ncirl.ie'
        },
        {
            'title': 'Blockchain Security and Consensus',
            'description': 'Study consensus mechanisms, security models, and attack vectors in blockchain systems. Learn PoW, PoS, and security auditing techniques.',
            'instructor_name': 'Dr. Stephanie Walker',
            'instructor_email': 'stephanie.walker@ncirl.ie'
        }
    ],
    'MSC-DT': [
        {
            'title': 'Digital Strategy and Innovation',
            'description': 'Learn to develop digital transformation strategies and drive innovation in organizations. Master strategic planning, innovation frameworks, and digital maturity models.',
            'instructor_name': 'Dr. Matthew Hall',
            'instructor_email': 'matthew.hall@ncirl.ie'
        },
        {
            'title': 'Digital Business Models',
            'description': 'Explore digital business models, platform economics, and value creation in digital ecosystems. Learn platform strategy, network effects, and digital monetization.',
            'instructor_name': 'Dr. Ashley Baker',
            'instructor_email': 'ashley.baker@ncirl.ie'
        },
        {
            'title': 'Change Management in Digital Transformation',
            'description': 'Understand organizational change management and leadership in digital transformation initiatives. Learn change models, stakeholder management, and cultural transformation.',
            'instructor_name': 'Dr. Joshua Wright',
            'instructor_email': 'joshua.wright@ncirl.ie'
        },
        {
            'title': 'Emerging Technologies and Trends',
            'description': 'Study emerging technologies, trends, and their impact on business transformation. Learn IoT, AI, blockchain, and their business applications.',
            'instructor_name': 'Dr. Samantha Hill',
            'instructor_email': 'samantha.hill@ncirl.ie'
        }
    ]
}

# Sample modules template for each course
SAMPLE_MODULES = [
    {
        'title': 'Introduction',
        'description': 'Course introduction, learning objectives, and overview of topics covered throughout the course.',
        'order': 1
    },
    {
        'title': 'Fundamentals',
        'description': 'Core concepts and fundamental principles that form the foundation of the subject matter.',
        'order': 2
    },
    {
        'title': 'Advanced Topics',
        'description': 'Advanced concepts, techniques, and applications building upon the fundamentals.',
        'order': 3
    },
    {
        'title': 'Practical Applications',
        'description': 'Hands-on projects, case studies, and real-world applications of the concepts learned.',
        'order': 4
    }
]

