aws_db = {
    "user": "admin",
    "password": "12345678",
    "host": "database-1.cf82kp3ku9xz.ap-northeast-2.rds.amazonaws.com",
    "port": "3306", # Maria DB의 포트
    "database": "sys",
}

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
JSON_AS_ASCII = False # 아직 test 못해봤음-jsonify 한글 보정
SQLALCHEMY_DATABASE_URI = f"mysql://{aws_db['user']}:{aws_db['password']}@{aws_db['host']}:{aws_db['port']}/\
{aws_db['database']}?charset=utf8"