import validators


def is_valid_url(url):
    return validators.url(url)


def is_len_valid(url):
    return len(url) <= 255
