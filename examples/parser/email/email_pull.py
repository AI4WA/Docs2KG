from Docs2KG.parser.email.utils.email_connector import EmailConnector

if __name__ == "__main__":
    email_address = ""
    password = ""
    imap_server = "imap.gmail.com"
    port = 993
    email_connector = EmailConnector(
        email_address=email_address,
        password=password,
        search_keyword="test search",
        num_emails=50,
        imap_server=imap_server,
        imap_port=port,
    )
    email_connector.pull()
