from aiohglib.util import b

changeset = b('{rev}\\0{node}\\0{tags}\\0{branch}\\0{author}\\0{desc}\\0{date|isodatesec}\\0{p1node}\\0{p2node}\\0{join(extras, \'_;_\')}\\0')

# This template use shortened description (super-long description can cause problems)
changeset_safe = b('{rev}\\0{node}\\0{tags}\\0{branch}\\0{author}\\0{fill(desc,200)|firstline}\\0{date|isodatesec}\\0{p1node}\\0{p2node}\\0{join(extras, \'_;_\')}\\0')

