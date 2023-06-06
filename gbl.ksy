meta:
  id: gbl
  endian: le
seq:
  - id: num_entries
    type: u4
  - id: entries
    type: entry
    repeat: expr
    repeat-expr: num_entries
types:
  entry:
    seq:
      - id: offset
        type: u4
      - id: len_data
        type: u4
    instances:
      data:
        pos: offset
        size: len_data