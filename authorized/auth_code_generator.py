import secrets
import string

def generate_auth_code(save_txt = False,length=16):
    """生成指定长度的复杂授权码
    Args:
        length (int): 授权码长度，默认为16位
        
    Returns:
        str: 生成的授权码
    """
    # 定义字符集，包含大小写字母、数字和特殊字符
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    # 使用secrets模块生成安全的随机字符串
    auth_code = ''.join(secrets.choice(characters) for _ in range(length))
    if save_txt:
        with open("./authorized/auth_code.txt", "a") as f:
            f.write( auth_code + '\n')
    return auth_code

# 示例用法
if __name__ == "__main__":
    # 生成一个16位的授权码并保存
    code = generate_auth_code(save_txt=True)
    print(f"生成的16位授权码: {code}")
    print("授权码已保存到 ./authorized/auth_code.txt 文件中")
    
    # 生成一个20位的授权码但不保存
    long_code = generate_auth_code(save_txt=False, length=20)
    print(f"生成的20位授权码: {long_code}")
    print("此授权码未保存到文件中")