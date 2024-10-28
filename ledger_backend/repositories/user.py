import bcrypt
#
from datetime import datetime
from sqlalchemy.orm import Session
#
from models.user import User
#
from abstractions.repository import IRepository

# The UserRepository class handles all database operations related to users,
# such as creating, updating, and retrieving user records based on various filters.
class UserRepository(IRepository):

    # Constructor that initializes the repository with parameters like URN, user URN, API name, and a database session.
    # The session is required to interact with the database. Raises an error if the session is missing.
    def __init__(self, urn: str = None, user_urn: str = None, api_name: str = None, session: Session = None):
        super().__init__(urn, user_urn, api_name)
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.session = session

        if not self.session:
            raise RuntimeError("DB session not found")
        
    # Method to create a new user record in the database.
    # Adds the user to the session and commits the transaction, logging the execution time.
    def create_record(self, user: User) -> User:

        start_time = datetime.now()
        self.session.add(user)
        self.session.commit()

        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return user

    # Method to retrieve a user record by email and password.
    # Filters the query based on the provided email, password, and whether the user is marked as deleted.
    def retrieve_record_by_email_and_password(
        self, 
        email: str, 
        password: str,
        is_deleted: bool = False
    ) -> User:

        start_time = datetime.now()
        record = self.session.query(User).filter(
            User.email == email, 
            User.password == password, 
            User.is_deleted == is_deleted
        ).first()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    # Method to retrieve a user record by email.
    # This method is useful when searching for users by their email address and checking if they are not deleted.
    def retrieve_record_by_email(
        self, 
        email: str,
        is_deleted: bool = False
    ) -> User:

        start_time = datetime.now()
        record = self.session.query(User).filter(
            User.email == email,
            User.is_deleted == is_deleted
        ).first()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None

    # Method to retrieve a user record by user ID.
    # This method checks if the user exists and is not deleted.
    def retrieve_record_by_id(self, id: str, is_deleted: bool = False) -> User:

        start_time = datetime.now()
        record = self.session.query(User).filter(User.id == id, User.is_deleted == is_deleted).first()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record if record else None
    
    # Method to retrieve a user record by ID and check if the user is logged in.
    # This method can be used to check the login status of a specific user.
    def retrieve_record_by_id_and_is_logged_in(self, id: str, is_logged_in: bool, is_deleted: bool = False) -> User:

        start_time = datetime.now()
        records = self.session.query(User).filter(User.id == id, User.is_logged_in == is_logged_in, User.is_deleted == is_deleted).all()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return records
    
    # Similar to the above, this method checks if a user is logged in based on the user's ID.
    # It retrieves only the logged-in user records, which is useful for authentication and session management.
    def retrieve_record_by_id_is_logged_in(self, id: int,  is_logged_in: bool, is_deleted: bool = False) -> User:

        start_time = datetime.now()
        record = self.session.query(User).filter(User.id == id, User.is_logged_in == is_logged_in, User.is_deleted == is_deleted).one_or_none()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return record
    
    # Method to retrieve all users who are currently logged in.
    # This is helpful for tracking active sessions in an application.
    def retrieve_record_by_is_logged_in(self, is_logged_in: bool, is_deleted: bool = False) -> User:

        start_time = datetime.now()
        records = self.session.query(User).filter(User.is_logged_in == is_logged_in, User.is_deleted == is_deleted).all()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return records
    
    # Method to update a user record in the database.
    # This method takes the user ID and a dictionary of new data to update the corresponding fields.
    def update_record(self, id: str, new_data: dict) -> User:

        start_time = datetime.now()
        user = self.session.query(User).filter(User.id == id).first()

        if not user:
            raise ValueError(f"User with id {id} not found")
        
        for attr, value in new_data.items():
            setattr(user, attr, value)

        self.session.commit()
        end_time = datetime.now()
        execution_time = end_time - start_time
        self.logger.info(f"Execution time: {execution_time} seconds")

        return user
