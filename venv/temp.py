
def main():
    cc_email = "kuwarjain394@gmail.com,devanshvashisht22@gmail.com"
    receiver_email = "ayaangautam@gmail.com"
    to_list = [receiver_email]
    if cc_email:
        if isinstance(cc_email, str):
            cc_list = [email.strip() for email in cc_email.split(",")]
        elif isinstance(cc_email, list):
            cc_list = cc_email
        else:
            cc_list = []
        to_list += cc_list
        print(to_list)
    else:
        cc_list = []



if __name__ == '__main__':
    main()