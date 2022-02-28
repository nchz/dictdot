from dictdot import dictdot

# doc in the code =)
code = "\n".join(line[4:] for line in dictdot.__doc__.split("\n")[1:])
exec(code + "print('ok!')")
