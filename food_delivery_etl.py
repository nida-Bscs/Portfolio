"""
Importing Libraries/Modules below
"""
import logging
import pandas as pd
import chardet
import sys
import time


import snowflake.connector
import os
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from snowflake.snowpark.exceptions import SnowparkSQLException


"""
Initializing Global Constant LOGGER_NAME underneath
"""
LOGGER_NAME='food_delivery_ETL'

"""Creating a Class named food_deilver_ETL below
which has its attributes initialized inside init constructor
It further has methods/functions created inside class.
"""

class food_delivery_ETL:
     def __init__(self):
        
        """ Initialize attributes like logging and file paths below"""
        self._logger=logging.getLogger(LOGGER_NAME)
        self.input_file_path=r"C:\Users\Admin\Downloads\archive\Order_delivery.csv"
        self.output_file_path=r"C:\Users\Admin\Downloads\archive\reencoded_Order_delivery.csv"
        self.transformed_file_path = (r"C:\Users\Admin\Downloads\archive\transformed_Order_delivery.csv")
        self.db_user=os.environ['SNOWFLAKE_USER']
        self.db_password=os.environ['SNOWFLAKE_PASSWORD']
        self.db_account=os.environ['SNOWFLAKE_ACCOUNT']
        self.db_warehouse='COMPUTE_WH'
        self.db_database_name='FOOD_DELIVERY_DB'
        self.db_schema_name='FOOD_DELIVERY_SC'
        self.db_role_name='ACCOUNTADMIN'
        self.db_table_name='FOOD_DELIVERY_DATASET'
       

     def detect_encoding(self):

         if not self.input_file_path:

           self._logger.warning(
            "Input file path is empty. Returning from detect_encoding()\n")

           return None

         try:

           with open(self.input_file_path, 'rb') as f:

              data = f.read(10000)

              result = chardet.detect(data)

           self._logger.info(
            f"Encoding of the csv file in detect_encoding() is: "
            f"{result['encoding']}\n"
        )

           return result['encoding']
         

         except FileNotFoundError:

           self._logger.error(
            f"File not found in detect_encoding(): "
            f"{self.input_file_path}\n")

         except PermissionError:

           self._logger.error(
            f"Permission denied to read file in detect_encoding(): "
            f"{self.input_file_path}\n")

         except Exception as e:

           self._logger.critical(
            f"Unexpected error in detect_encoding(): {e}\n"
        )

        
           return None
     def detect_output_encoding(self):
       if not self.output_file_path:
        self._logger.warning(
            "Output file path is empty."
        )
        return None

       try:
        with open(self.output_file_path, 'rb') as f:
            data = f.read(10000)

        result = chardet.detect(data)

        self._logger.info(
            f"Encoding of output CSV: {result['encoding']}"
        )

        return result['encoding']

       except FileNotFoundError:
        self._logger.error("Output CSV file not found.")
        return None

       except Exception as e:
         self._logger.error(
            f"Error detecting output encoding: {e}"
        )
         return None
         
     
     def write_csv_data(self, encd: str):

      if not self.input_file_path:
        self._logger.warning(
            "Input file path is empty. "
            "Returning from write_csv_data()\n"
        )
        return

      elif not self.output_file_path:
        self._logger.warning(
            "Output file path is empty. "
            "Returning from write_csv_data()\n"
        )
        return

      try:
        with open(
            self.input_file_path,
            'r',
            encoding=encd,
            errors='replace'
        ) as infile:

            with open(
                self.output_file_path,
                'w',
                encoding='utf-8',
                newline=''
            ) as outfile:

                for line in infile:
                    outfile.write(line)

        # Verify output can be decoded as UTF-8
        with open(
            self.output_file_path,
            'r',
            encoding='utf-8'
        ) as f:
            f.read()

        self._logger.info(
            "Output file successfully decoded as UTF-8."
        )

      except FileNotFoundError:
        self._logger.error(
            f"File not found: {self.input_file_path}\n"
        )

      except PermissionError:
        self._logger.error(
            f"Permission denied to read or write file: "
            f"{self.input_file_path}\n"
        )

      except UnicodeDecodeError:
        self._logger.error(
            f"Error while reading the file with encoding: "
            f"{encd}\n"
        )

      except Exception as e:
        self._logger.critical(
            f"Unexpected error in write_csv_data(): {e}\n"
        )

         
         
     def extract_csv_data(self, encd: str):
         try:
            self.write_csv_data(encd)

            df = pd.read_csv(self.output_file_path, encoding='utf-8')

            self._logger.info("CSV data extracted successfully.")

            print(df.head())

            return df

         except FileNotFoundError:
            self._logger.error("CSV file not found.")

         except pd.errors.EmptyDataError:
            self._logger.error("CSV file is empty.")

         except Exception as e:
            self._logger.error(f"Error in extract_csv_data(): {e}")
       
     def transform_data(self, df: pd.DataFrame) ->pd.DataFrame:

        if df is None or df.empty:
         self._logger.warning(
            "DataFrame is empty. "
            "Returning from transform_data()."
         )
         return None

        self._logger.info(
        "Starting data transformation."
        )

      # Inspect column names, data types, and non-null values
       # df.info()

      # Count missing values in each column
        print("\nMissing values in each column:")
        print(df.isnull().sum())
         # Check duplicate rows
        duplicate_count = df.duplicated().sum()

        print("\nTotal duplicate rows:", duplicate_count)

        self._logger.info(
        f"Total duplicate rows: {duplicate_count}"
        )
        print("\nData types of each column:")
        print(df.dtypes)

        # Convert Order_Time and Delivery_Time to datetime
        datecols=[col for col in df.columns if "date" in col.lower()]
        for col in datecols:
                df[col]=pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                
            # Logs data types after converting date columns
        self._logger.info(f"Current Datatypes of all columns in transform():\n\n{df.dtypes}\n\n")



            # Converts object columns to string type dynamically
        df[df.select_dtypes(include=['object']).columns]=df.select_dtypes(include=['object']).astype('string')

        # Log data types after conversion
        self._logger.info(
        f"Current datatypes of Order_Time and Delivery_Time:\n"
        f"{df[datecols].dtypes}"
        )

        # Display values in YYYY-MM-DD HH:MM:SS format
        print("\nUpdated data types:")
        print(df[datecols].dtypes)

        print("\nFormatted date and time values:")
        print(
         df[datecols].head().to_string(
         formatters={
            col: lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
            if pd.notna(x) else ''
            for col in datecols
         }
         )
         )
        
        

        
        return df
     
     

        
     def table_exists(self, session):
        query=f"""
        SELECT COUNT(*)
        FROM FOOD_DELIVERY_DB.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = '{self.db_schema_name.upper()}'
        AND TABLE_NAME = '{self.db_table_name.upper()}'
        """
        #Executes the SQL query using the provided session and collect the results.
        result=session.sql(query).collect()
        #Returns True if the table exists (i.e., COUNT(*) > 0), otherwise return False.
        return result[0][0] > 0
     

     def load_to_snowflake(self, df:pd.DataFrame):
        try:
            #Log the DataFrame's column names before writing to Snowflake
            cols_list=df.columns.tolist()
            self._logger.info(f"Dataframe columns before writing in load_to_snowflake():\n{cols_list}\n")

            #Log a message before creating a Snowflake session
            self._logger.info("Before creating snowflake session in load_to_snowflake()\n")

            #Create a Snowflake session using provided credentials and configuration
            session=Session.builder.configs({
                "user":self.db_user,
                "password":self.db_password,
                "account":self.db_account,
                "warehouse":self.db_warehouse,
                "database":self.db_database_name,
                "schema":self.db_schema_name,
                "role":self.db_role_name
            }).create()
            self._logger.info("Snowflake session successfully created in load_to_snowflake()\n")
            if self.table_exists(session):
                #Dynamically adding columns into the table so if schema of file changes, snowflake will also be updated with the same schema without any errors
                self._logger.info(f"Table  \"{self.db_table_name}\" exists in database in load_to_snowflake()\n")

                #Query the schema of the existing table
                query=f"DESCRIBE TABLE \"{self.db_table_name}\""
                table_schema=session.sql(query).collect()

                #Extract column names from the table schema
                table_cols=[row['name'].lower() for row in table_schema]
                self._logger.info(f"Table column in database in load_to_snowflake():\n{table_cols}\n")

                #Identify missing columns in existing table compared to the DataFrame
                missing_cols=[col for col in df.columns if col.lower() not in table_cols]
                if missing_cols:
                    #Log missing columns and add them to Snowflake table
                    self._logger.warning(f"Snowflake db table has missing columns in load_to_snowflake():\n{missing_cols}\n")
                    for col in missing_cols:
                        alter_table_query=f"ALTER TABLE \"{self.db_table_name}\" ADD COLUMN \"{col}\" STRING"
                        session.sql(alter_table_query).collect()
                        self._logger.info(f"Added columns in snowflake db in load_to_snowflake():\n{df.columns.tolist()}\n")
            #Measure the time taken to write the DataFrame to Snowflake
            start_time=time.time()

            session.sql(
             f'DROP TABLE IF EXISTS "{self.db_table_name}"'

            ).collect()
            #Write the DataFrame directly to Snowflake table, overwriting any existing data in the table
            session.write_pandas(
                df,
                table_name=self.db_table_name,
                auto_create_table=True,
                overwrite=True
            )

            #Log the elapsed time for the data load operation
            elapsed_time=time.time()-start_time
            self._logger.info(f"Table created and data loaded into snowflake in {self.db_table_name} in {elapsed_time:2f} seconds in load_to_snowflake()\n")
        except SnowparkSQLException as e:
            #Log critical errors for Snowflake SQL exceptions
            self._logger.critical(f"Snowflake sql error in load_to_snowflake(): {e}\n")
        except Exception as e:
            #Log critical errors for general exceptions
            self._logger.critical(f"Exception occurred in load_to_snowflake(): {e}\n")
        finally:
            #Close the Snowflake session and log the action
            session.close()
            self._logger.info("Session closed successfully in load_to_snowflake()\n")

     
     def load_csv_data(self, df: pd.DataFrame):

        if df is None or df.empty:
          self._logger.warning(
            "DataFrame is empty. Nothing to save."
        )
          return

        try:
          df.to_csv(
             self.transformed_file_path,
            index=False,
            encoding='utf-8'
        )

          self._logger.info(
            f"Transformed data saved successfully: "
            f"{self.transformed_file_path}"
        )

        except Exception as e:
          self._logger.error(
            f"Error saving transformed data: {e}"
        )

    
     
     def run(self):
       try:
            #Configure logging to include timestamp, logger name and log level
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            #Logs the start of the ETL Process
            self._logger.info("Started Food Delivery ETL in run()\n")

            #Sets pandas display options for better visualization of large DataFrames
            pd.set_option('display.max_rows', 20)
            pd.set_option('display.max_columns', None)

            #Detects the encoding of the input CSV File
            encd=self.detect_encoding()
            #Extracts data from CSV File into a pandas dataframe 
            df=self.extract_csv_data(encd)

            #Checks if the DataFrame is empty, logs a warning then exits if it is empty
            if df.empty:
                self._logger.warning("Dataframe is empty. Exiting netflix from run()\n")
                return
            else:
                #Transforms the dataframe to remove duplicates, drop unnamed columns and handle misising columns
                df_t = self.transform_data(df)
                #Save transformed data to CSV
                self.load_csv_data(df)
                sys.stdout.flush()
                sys.stderr.flush()
                self.load_to_snowflake(df_t)
       except Exception as e:
            #Logs a critical error message for any unexpected exception
            self._logger.critical(f"Exception occurred in run(): {e}\n")

         
if __name__ == '__main__':

 food_delivery = food_delivery_ETL()

 food_delivery.run()