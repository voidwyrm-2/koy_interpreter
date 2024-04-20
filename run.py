from pathlib import Path
import main



def grabfile(path: str):
    if not Path(path + '.koy').exists(): print(f'file "{path}" does not exist'); return
    with open(path + '.koy', 'rt') as filein: return filein.read()


filename = 'stdin'
running = True
while running:
    inp = input('>>> ')
    if inp == 'exit': running = False; break
    
    if inp.startswith('file '):
        filecontents = grabfile(inp.removeprefix('file ').strip().removesuffix('.koy').strip())
        if filecontents != None: filename = inp.removeprefix('file ').split('/')[-1]

    result, error = main.run(filename, filecontents)

    if error: print(error.as_string())
    else: print(result)