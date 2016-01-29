import re

def filter(str):
    pattern = re.compile(r'%7B%22ip%22%3A%22(.*?)%22%2C%22port%22%3A%22(.*?)%22%7D%2C')
    match = pattern.findall(str, re.S)
    result = pattern.finditer(str)

    if result is None:
        print 'no match'
        return

    filter_str = []

    print '\n\nresult is:'
    for m in result:
        print '%s:%s' % (m.group(1), m.group(2))
        filter_str.append('tcp.port==')
        filter_str.append(m.group(2))
        filter_str.append('||')

    print '\n\nfilter string is: '
    print ''.join(filter_str)[:-2]+'&&tcp.flags.push==1'

if __name__ == '__main__':
    input_str = raw_input("enter the original string: \n")
    if input_str is None:
        print 'input is null !'
    else:
        filter(input_str)




