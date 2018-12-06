from read_and_write_data import read_data, read_field_size


def linear(list_of_tuples, field_size, print_result=False):
    resulting_share = 0
    for (scalar, share) in list_of_tuples:
        resulting_share = (resulting_share + scalar * share) % field_size
    if print_result:
        print("Linear result is:", resulting_share)
    return resulting_share
