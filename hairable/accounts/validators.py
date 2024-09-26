from .models import User

def validate_user_data(user_data):
    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")
    phone = user_data.get("phone")
    birthday = user_data.get("birthday")
    gender = user_data.get("gender")
    introduction = user_data.get("introduction")


    err_msg = []

    if not username:
        err_msg.append("닉네임은 필수 값입니다.")
    if not email:
        err_msg.append("이메일은 필수 값입니다.")
    if not password:
        err_msg.append("패스워드는 필수 값입니다.")
    if not phone:
        err_msg.append("전화번호는 필수 값입니다.")
    if not birthday:
        err_msg.append("생일은 필수 값입니다.")

    if username and len(username) < 2:
        err_msg.append("닉네임이 너무 짧습니다.")

    if password and len(password) < 8:
        err_msg.append("비밀번호가 너무 짧습니다")

    if username and User.objects.filter(username=username).exists():
        err_msg.append("이미 존재하는 username 입니다")

    if email and User.objects.filter(email=email).exists():
        err_msg.append("이미 존재하는 email입니다")

    return err_msg