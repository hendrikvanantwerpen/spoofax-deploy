def YesNo(message = None):
  if message != None:
    print(message + ' [Y/n]')
  else:
    print('[Y/n]')
  choice = input()
  if choice != 'Y':
    return False
  return True

def YesNoTwice():
  if YesNo():
    return YesNo("Are you really really sure?")
  return False

def YesNoTrice():
  if YesNo():
    if YesNo("Are you really really sure?"):
      return YesNo("Are you really really really really sure?")
  return False
