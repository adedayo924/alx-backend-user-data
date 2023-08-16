#!/usr/bin/env python3
"""obfuscator"""
from typing import List, Tuple
import re
import logging
from os import getenv
import mysql.connector as db

mysql_config = {
    "username": getenv("PERSONAL_DATA_DB_USERNAME") or "root",
    "password": getenv("PERSONAL_DATA_DB_PASSWORD") or "",
    "host": getenv("PERSONAL_DATA_DB_HOST") or "localhost",
    "database": getenv("PERSONAL_DATA_DB_NAME")
}

PII_FIELDS: Tuple[str, str, str, str, str] = (
    "name",
    "email",
    "phone",
    "ssn",
    "password"
)


def get_db() -> db.connection.MySQLConnection:
    """Return a Mysql connection"""
    return db.connect(**mysql_config)


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """Returns message string with the required fields obfuscated"""
    os = message
    for i in fields:
        os = re.sub(rf"{i}=(.+?)(?={separator})", f"{i}={redaction}", os)
    return os


def get_logger() -> logging.Logger:
    """Return a Logger instance"""
    logger: logging.Logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler: logging.StreamHandler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(handler)
    return logger


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """returns formated string"""
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


def main() -> None:
    db = get_db()
    cursor = db.cursor(dictionary=True)
    logger = get_logger()

    fields = ["name", "email", "phone", "ssn",
              "password", "ip", "last_login", "user_agent"]

    query = """SELECT name, email, phone, ssn, password,
               ip, last_login, user_agent FROM users"""
    cursor.execute(query)
    for i in cursor.fetchall():
        log = ""
        for j in fields:
            log += f"{j}={i[j]}; "
        logger.info(log)
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
