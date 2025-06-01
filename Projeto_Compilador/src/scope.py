class Scope:
  def __init__(self):
      self.scopes = list()
      self.scopes.append({'label': 'global', 'next_index': 0, 'vars': dict()})
  
  def push(self):
      self.scopes.append({'label': 'local', 'next_index': 0, 'vars': dict()})
  
  def pop(self):
    if len(self.scopes) == 1:
      raise Exception("Já no escopo global; não há escopo para sair.")
    self.scopes.pop()

  def declare(self, name):
    current_scope = self.scopes[-1]
    if name in current_scope['vars']:
      raise Exception(f"Variable '{name}' already declared in current scope.")
    idx = current_scope['next_index']
    current_scope['vars'][name] = idx
    current_scope['next_index'] += 1
    return idx
  
  def lookup(self, name) -> int | None:
    for scope in reversed(self.scopes):
      if name in scope['vars']:
        return scope['vars'][name]
    return None
    
