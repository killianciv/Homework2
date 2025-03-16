import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import datetime
class database:

    def __init__(self, purge = False):
        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'

    def query(self, query = "SELECT CURDATE()", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )

        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def about(self, nested=False):
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        print('I created and populated database tables.')
        # Create institutions > positions > experiences > skills because of foreign key dependence

        # Create the table 'institutions' and populate with .csv initial data
        sql_file_path = data_path + 'create_tables/institutions.sql'
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()  # Reads institutions.sql into a string
            self.query(sql_script)  # Passes it to query()
        csv_file_path = data_path + 'initial_data/institutions.csv'
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)  # Skip the column names that are the first row
            # Insert each .csv line as a row in the table
            for row in csv_reader:
                if not row:  # Skip empty rows
                    continue
                # Skips 'inst_id' (first thing) since it's auto-incrementing. 'NULL' --> None
                vals = [None if val.strip().upper() == 'NULL' else val.strip() for val in row[1:]]
                # Check if the institution already exists (based on `type` and `name`).
                # NULL cannot be tested for using equality, so I do want to
                #   check equality using columns with the NOT NULL constraint only
                #   or else queries are much longer, like AND (department = %s OR department IS NULL)
                existing_inst = self.query("""SELECT 1 FROM institutions 
                                                              WHERE type = %s AND name = %s""",
                                           parameters=(vals[0], vals[1]))  # Using indexes from `vals`
                if not existing_inst:  # Only insert if the institution doesn't already exist
                    self.query("""INSERT INTO institutions (type, name, department, address, city, state, zip)
                                                  VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                               parameters=tuple(vals))

        # Create the table 'positions' and populate with .csv initial data
        sql_file_path = data_path + 'create_tables/positions.sql'
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            self.query(sql_script)
        csv_file_path = data_path + 'initial_data/positions.csv'
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                if not row:
                    continue
                # Skips 'position_id' (first thing) since it's auto-incrementing.
                vals = [None if val.strip().upper() == 'NULL' else val.strip() for val in row[1:]]
                # Check if the position already exists based on `inst_id`, `title`, and `start_date`
                existing_pos = self.query("""SELECT 1 FROM positions 
                                                             WHERE inst_id = %s AND title = %s AND start_date = %s""",
                                          parameters=(vals[0], vals[1], vals[3]))
                if not existing_pos:
                    self.query("""INSERT INTO positions (inst_id, title, responsibilities, start_date, end_date)
                                                  VALUES (%s, %s, %s, %s, %s)""",
                               parameters=tuple(vals))

        # Create the table 'experiences' and populate with .csv initial data
        sql_file_path = data_path + 'create_tables/experiences.sql'
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            self.query(sql_script)
        csv_file_path = data_path + 'initial_data/experiences.csv'
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                if not row:
                    continue
                # Skips 'experience_id' (first thing) since it's auto-incrementing.
                vals = [None if val.strip().upper() == 'NULL' else val.strip() for val in row[1:]]
                # Check if the experience already exists based on `position_id` and `name`
                existing_exp = self.query("""SELECT 1 FROM experiences 
                                                            WHERE position_id = %s AND name = %s""",
                                          parameters=(vals[0], vals[1]))
                if not existing_exp:
                    self.query("""INSERT INTO experiences (position_id, name, description, hyperlink, start_Date, end_date)
                                                  VALUES (%s, %s, %s, %s, %s, %s)""",
                               parameters=tuple(vals))

        # Create the table 'skills' and populate with .csv initial data
        sql_file_path = data_path + 'create_tables/skills.sql'
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            self.query(sql_script)
        csv_file_path = data_path + 'initial_data/skills.csv'
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                if not row:
                    continue
                # Skips 'skill_id' (first thing) since it's auto-incrementing.
                vals = [None if val.strip().upper() == 'NULL' else val.strip() for val in row[1:]]
                # Check if the skill already exists based on `experience_id` and `name`
                existing_skill = self.query("""SELECT 1 FROM skills 
                                                              WHERE experience_id = %s AND name = %s""",
                                            parameters=(vals[0], vals[1]))
                if not existing_skill:
                    self.query("""INSERT INTO skills (experience_id, name, skill_level)
                                                  VALUES (%s, %s, %s)""",
                               parameters=tuple(vals))

        # Create the table 'feedback'. No initial data
        sql_file_path = data_path + 'create_tables/feedback.sql'
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            self.query(sql_script)

        # Test: Print the tables
        print("\nInstitutions entries:")
        print(self.query("""SELECT * FROM institutions"""))
        print("\nPositions entries:")
        print(self.query("""SELECT * FROM positions"""))
        print("\nExperiences entries:")
        print(self.query("""SELECT * FROM experiences"""))
        print("\nSkills entries:")
        print(self.query("""SELECT * FROM skills"""))
        print("\nFeedback entries:")
        print(self.query("""SELECT * FROM feedback"""))

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        print('I Inserted rows into the database.')
        # Make an INSERT INTO statement that makes a new record with the parameter sub-list
        #   values for the two specified columns
        if len(columns) != len(parameters[0]):
            raise ValueError("Number of columns does not match the number of values in parameters.")

        # Comma-separated strings. Turned into tuples via the () in the query
        column_names = ', '.join(columns)  # 'x, y'
        placeholders = ', '.join(['%s'] * len(columns))  # '%s, %s'
        # Dynamic SQL query. Ignore the command if the primary key constraint is violated
        query = f"INSERT IGNORE INTO {table} ({column_names}) VALUES ({placeholders})"

        # Insert each row, ensuring NULL handling and proper formatting
        for new_row in parameters:
            # Convert 'NULL' string values to Python None, clean other values
            formatted_row = []
            for val in new_row:
                if isinstance(val, str):
                    # If the value is a string, check for 'NULL' and strip
                    formatted_row.append(None if val.strip().upper() == 'NULL' else val.strip())
                else:
                    # If the value is not a string (e.g., int), append it directly
                    formatted_row.append(val)

            # Make sure to convert the formatted row to a tuple and pass it as parameters
            self.query(query, parameters=tuple(formatted_row))


    def getResumeData(self):
        # Pulls data from the database to generate data like this (hardcoded):
        # return {1: {'address': 'NULL',
        #             'city': 'East Lansing',
        #             'state': 'Michigan',
        #             'type': 'Academia',
        #             'zip': 'NULL',
        #             'department': 'Computer Science',
        #             'name': 'Michigan State University',
        #             'positions': {1: {'end_date': None,
        #                               'responsibilities': 'Teach classes; mostly NLP and Web design.',
        #                               'start_date': datetime.date(2020, 1, 1),
        #                               'title': 'Instructor',
        #                               'experiences': {1: {'description': 'Taught an introductory course ... ',
        #                                                   'end_date': None,
        #                                                   'hyperlink': 'https://gitlab.msu.edu',
        #                                                   'name': 'CSE 477',
        #                                                   'skills': {},
        #                                                   'start_date': None
        #                                                   },
        #                                               2: {'description': 'introduction to NLP ...',
        #                                                   'end_date': None,
        #                                                   'hyperlink': 'NULL',
        #                                                   'name': 'CSE 847',
        #                                                   'skills': {1: {'name': 'Javascript',
        #                                                                  'skill_level': 7},
        #                                                              2: {'name': 'Python',
        #                                                                  'skill_level': 10},
        #                                                              3: {'name': 'HTML',
        #                                                                  'skill_level': 9},
        #                                                              4: {'name': 'CSS',
        #                                                                  'skill_level': 5}},
        #                                                   'start_date': None
        #                                                   }
        #                                               }}}}}


        # This query will give me one row for each institution. Table is renamed i.
        query = """
            SELECT 
                i.inst_id, i.type, i.name, i.department, i.address, i.city, i.state, i.zip,
                p.position_id, p.title, p.responsibilities, p.start_date AS position_start, 
                p.end_date AS position_end,
                e.experience_id, e.name AS experience_name, e.description, e.hyperlink,
                e.start_date AS experience_start, e.end_date AS experience_end,
                s.skill_id, s.name AS skill_name, s.skill_level
            FROM institutions i
            LEFT JOIN positions p ON i.inst_id = p.inst_id
            LEFT JOIN experiences e ON p.position_id = e.position_id
            LEFT JOIN skills s ON e.experience_id = s.experience_id
        """
        # Left join to include institutions that temporarily have no positions
        # Alias table names for shortness, alias column names for clarity

        results = self.query(query)  # Fetch data from the database
        resume_data = {}  # Dictionary to store hierarchical structure
        # I will also have a new dictionary inside each dictionary that
        #   stores the contents of its child table. For example, institutions
        #   stores a dictionary of positions, and so on.

        # Results is a dictionary that maps a row to all the column values in that row.
        for row in results:
            # Build the institution Level of my custom, fully-informative resume_data dictionary
            inst_id = row["inst_id"]
            if inst_id not in resume_data:
                resume_data[inst_id] = {
                    "type": row["type"],
                    "name": row["name"],
                    "department": row["department"],
                    "address": row["address"],
                    "city": row["city"],
                    "state": row["state"],
                    "zip": row["zip"],
                    "positions": {}  # Store positions inside the institution
                }

            # Position level (filling in the "positions": {} dictionary with some columns' data)
            position_id = row["position_id"]
            if position_id and position_id not in resume_data[inst_id]["positions"]:
                resume_data[inst_id]["positions"][position_id] = {
                    "title": row["title"],
                    "responsibilities": row["responsibilities"],
                    "start_date": row["position_start"],
                    "end_date": row["position_end"],
                    "experiences": {}  # Store experiences inside the position
                }

            # Experience level
            experience_id = row["experience_id"]
            if experience_id and experience_id not in resume_data[inst_id]["positions"][position_id]["experiences"]:
                resume_data[inst_id]["positions"][position_id]["experiences"][experience_id] = {
                    "name": row["experience_name"],
                    "description": row["description"],
                    "hyperlink": row["hyperlink"],
                    "start_date": row["experience_start"],
                    "end_date": row["experience_end"],
                    "skills": {}  # Store skills inside the experience
                }

            # Skill level
            skill_id = row["skill_id"]
            if skill_id:
                resume_data[inst_id]["positions"][position_id]["experiences"][experience_id]["skills"][skill_id] = {
                    "name": row["skill_name"],
                    "skill_level": row["skill_level"]
                }

        return resume_data



