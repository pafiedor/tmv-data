"""Recompute the browser-side checksum for each '### <key> ... checksum=' block.
Browser algorithm: for every cell, first regex match of -?\d+(\.\d+)? after removing
commas, absolute value, summed over all cells including header cells."""
import re, sys
def num(s):
    m = re.search(r'-?\d+(\.\d+)?', s.replace(',', ''))
    return abs(float(m.group(0))) if m else 0.0
for path in sys.argv[1:]:
    txt = open(path, encoding='utf-8').read()
    blocks = re.split(r'\n### ', '\n' + txt)[1:]
    for b in blocks:
        head, _, body = b.partition('\n')
        if 'checksum=' not in head:
            continue
        want = float(re.search(r'checksum=([\d.]+)', head).group(1))
        body = body.split('\n\n')[0]
        got = 0.0
        for line in body.strip('\n').split('\n'):
            for cell in line.split(' | '):
                got += num(cell)
        status = 'OK ' if abs(got - want) < 0.01 else 'MISMATCH'
        print(f'{status} {path} {head.split()[0]} want={want:.2f} got={got:.2f}')
