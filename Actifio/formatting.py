from functools import wraps

class ActFormatter():

  @classmethod
  def default_format(cls, dict_input):
    return dict_input

  _formatter = default_format

  @classmethod
  def decorate (cls, formatter_func, **kwargs):
    @wraps(formatter_func)
    def wprapper_func():
      return ActFormatter._formatter(formatter_func(**kwargs))
    return wprapper_func

  @classmethod
  def default_format(cls, dict_input):
    return dict_input

  @classmethod
  def fixedwidth_format(cls, values):
    table = []
    header = []
    max_width = []

    output = ''

    for hitem in values['result'][0]:
        header.append(hitem)
        table.append([hitem, []])
        max_width.append([hitem, 0])

    for item in values['result']:
        for key, val in enumerate(table):
            table[key][1].append(item[val[0]])
            if max_width[key][1] == 0:
                max_width[key][1] = len(item[val[0]])
            elif max_width[key][1] < len(item[val[0]]):
                max_width[key][1] = len(item[val[0]])
            # print "%s legth: %d"%(val,max_width[key][1])
    
    # Print the headers
    for cols , hitem in enumerate(table):
        output += str(hitem[0]).ljust(max_width[int(cols)][1]+5) + '\t'
    output += "\n"
    for cols , hitem in enumerate(table):
        output += str('-').ljust(max_width[int(cols)][1]+5, '-') + '\t'
    output += "\n"

    for rows, vals in enumerate(table[0][1]):
        for cols, item in enumerate(table):
            output += str(item[1][int(rows)]).ljust(max_width[int(cols)][1]+5) + '\t' 
        output += "\n"
    
    return output

