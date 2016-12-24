#!python3
import re
import argparse
import os

COLUMN_MAX = 79

class Parser:
   def _transform_to_arr(self):
      arr = []
      keep_going = True
      next_tok = '' if self._pds else ' '
      first_line = True

      while keep_going:
         def add_on_and_count(s):
            nonlocal col_cnt
            nonlocal arr
            arr[-1] += s
            col_cnt += len(s)

         col_cnt = 0
         arr.append('')

         add_on_and_count(self._indent)
         if not self._pds or first_line:
            add_on_and_count(self._comment_char)
         add_on_and_count(next_tok)

         while True:
            try:
               next_tok = next(self._word_iter).group()
               if not first_line:
                  next_tok = ' ' + next_tok
            except StopIteration:
               keep_going = False
               break

            if col_cnt + len(next_tok) > COLUMN_MAX:
               if self._pds:
                  next_tok = re.sub(r'^\s*', '', next_tok)
               break

            arr[-1] += next_tok
            col_cnt += len(next_tok)
            first_line = False

      if self._pds:
         arr.append(self._indent + self._comment_char)

      return arr

   def __init__(self, filename):

      with open(filename, 'r') as comment_file:
         comments = comment_file.read()

      beginning = re.match(r'^(\s*)([^\w\s]+)', comments)
      self._indent = re.sub(r'\n*', '', beginning.group(1))
      self._comment_char = beginning.group(2)
      self._pds = True if self._comment_char == '"""' else False
      self._comments = re.sub(re.escape(self._comment_char), '', comments)
      self._word_iter = re.finditer(r'\S+', self._comments)

   @property
   def indent(self):
      return self._indent

   @property
   def comment_char(self):
      return self._comment_char

   def get_lines(self):
      for l in self._transform_to_arr():
         yield l

def main():
   arg_parser = argparse.ArgumentParser(
      description='Keeps comments under |n| columns')
   arg_parser.add_argument('-n', '--num-col', type=int,
      help='width as column number. Default is 79.')
   arg_parser.add_argument('INPUT_FILE', help='file containing comments')
   args = arg_parser.parse_args()

   global COLUMN_MAX
   if args.num_col:
      COLUMN_MAX = args.num_col

   parser = Parser(args.INPUT_FILE)
   lines = parser.get_lines()
   with open(args.INPUT_FILE + '.tmp', 'w') as output:
      for line in lines:
         output.write(line + "\n")
   os.rename(args.INPUT_FILE + '.tmp', args.INPUT_FILE)

if __name__ == '__main__':
   main()
