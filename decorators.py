# Decorator to handle errors for functions in processing.py
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f'ValueError: {str(e)}'
        except IndexError:
            return 'IndexError: Insufficient arguments provided.'
        except KeyError:
            return 'KeyError: Contact not found.'
    return inner