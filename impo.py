import tkinter as tk

BUCKET_SIZE = 47  # FR
NB = 10_000

indexes = [{} for b in range(NB)]

def hash_(k):
    hs = 0
    for n in k:
        character = ord(n)
        hs = ((hs << 5) - hs) + character
    return abs(hs) % NB

def get_page_number_by_key(k):
    '''
    Input: the key to search
    Returns # of iter and the page number
    '''
    id = hash_(k)
    iterations = 0
    for key, value in indexes[id].items():
        iterations += 1
        if k in value:
            return iterations, indexes[id][key][k]
    return iterations, None

class Page:
    overflow = 0
    collision = 0
    page_size = 2
    def __init__(self):
        self.page = []
    
    @property
    def num_of_pages(self):
        return len(self.page)

    def number_of_objects(self):
        if len(self.page[-1]) == self.page_size:
            return self.page_size * self.num_of_pages
        return self.page_size * (self.num_of_pages - 1) + len(self.page[-1])
    
    def table_scan(self, limit=100):
        iteration = 0
        for obj_ in self.page:
            for element in obj_:
                iteration += 1
                if iteration == limit:
                    return iteration
        return iteration

    def table_scan_find(self, search):
        iteration = 0
        num_pages = 0
        for obj_ in self.page:
            num_pages += 1
            for element in obj_:
                iteration += 1
                if search == element:
                    return element, iteration, num_pages
        return None, iteration, num_pages

    
    def get_element_from_index(self, k):
        '''
        Input: key to find in table
        Returns the # of iter and the object
        '''
        iterations, page_number = get_page_number_by_key(k)
        if not page_number:
            return iterations, None
        current_page = self.page[page_number]
        for el in current_page:
            iterations += 1
            if el == k:
                return iterations, el
        return iterations, None

    def insert(self):
        '''
        Inserts objects in the DB.
        Populates index.
        '''
        f = open('words.txt', 'r')
        build_page = []
        i = 0
        for line in f:
            key = line.strip('\n')
            build_page.append(key)
            page_number = len(self.page)
            if len(indexes[hash_(key)]) == 0:
                indexes[hash_(key)][1] = {key: page_number}
            else:
                # Get last overflow in dict
                last_overflow = list(indexes[hash_(key)])[-1]
                if len(indexes[hash_(key)][last_overflow]) == BUCKET_SIZE:
                    self.overflow += 1
                    self.collision += 1
                    indexes[hash_(key)][last_overflow + 1] = {}
                    indexes[hash_(key)][last_overflow + 1][key] = page_number
                else:
                    if last_overflow > 1:
                        self.collision += 1
                    indexes[hash_(key)][last_overflow][key] = page_number
            
            if i == self.page_size - 1:
                self.page.append(build_page)
                i = -1
                build_page = []
            i += 1
        if build_page and (i > 0):
            self.page.append(build_page)
        # print(self.page)

obj = Page()

def update_page_size():
    ps = int(page_size_input.get('1.0','end-1c').strip('\n'))
    page_size_result['text'] = f'Tamanho da página: {ps}'
    obj.page_size = ps

def table_scan_start():
    limit = int(table_scan_limit.get('1.0','end-1c').strip('\n'))
    table_scan_result['text'] = f'Número de iterações ao trafegar: {obj.table_scan(limit=limit)}'

def table_scan_search_fn():
    search = table_scan_search_input.get('1.0','end-1c').strip('\n')
    print(search)
    found, iterations, num_pages = obj.table_scan_find(search=search)
    if found:
        table_scan_search_result['text'] = f'Encontrado | {iterations} iterações | # Páginas: {num_pages}'
    else:
        table_scan_search_result['text'] = f'Não encontrado | {iterations} iterações | # Páginas: {num_pages}'

def table_insert():
    obj.insert()
    overflow_label['text'] = f'Overflow: {obj.overflow}'
    collision_label['text'] = f'Colisão: {obj.collision} | {(obj.collision/obj.number_of_objects())*100.0:.2f}%'
    print(f'tamanho pagina = {len(obj.page[0])}')

def index_search_fn():
    search = index_search_input.get('1.0','end-1c').strip('\n')
    print(search)
    iterations, found = obj.get_element_from_index(k=search)
    if found:
        index_search_result['text'] = f'Encontrado | {iterations} iterações'
    else:
        index_search_result['text'] = f'Não encontrado | {iterations} iterações'

window = tk.Tk()
window.title('Banco de Dados')

## Row 0 ##
page_size_label = tk.Label(
    window,
    text='Tamanho da página',
)
page_size_label.grid(row=0, column=0)
page_size_input = tk.Text(
    window,
    height = 2,
    width = 10,
)
page_size_input.grid(row=0, column=1)

page_size_button = tk.Button(
    window,
    text='Salvar',
    command=update_page_size,
)
page_size_button.grid(row=0, column=2)

## Row 1 ##
page_size_result = tk.Label(
    window,
    text='Tamanho da página:',
)
page_size_result.grid(row=1, column=0)

bucket_size_label = tk.Label(
    window,
    text=f'Tamanho do bucket: {BUCKET_SIZE}',
)
bucket_size_label.grid(row=1, column=1)

insert_button = tk.Button(
    window,
    text='Inserir dados',
    command=table_insert,
)
insert_button.grid(row=1, column=2)

## Row 2 ##
overflow_label = tk.Label(window, text='Overflow:')
overflow_label.grid(row=2, column=0)
collision_label = tk.Label(window, text='Colisão:')
collision_label.grid(row=2, column=1)

## Row 3 ##
table_scan_label = tk.Label(
    window,
    text='Table scan de:',
)
table_scan_label.grid(row=3, column=0)
table_scan_limit = tk.Text(
    window,
    height = 2,
    width = 10,
)
table_scan_limit.grid(row=3, column=1)

table_scan_button = tk.Button(
    window,
    text='Começar Table Scan',
    command=table_scan_start,
)
table_scan_button.grid(row=3, column=2)

## Row 4 ##
table_scan_result = tk.Label(window, text='')
table_scan_result.grid(row=4, column=0)

## Row 5 ##
table_scan_search = tk.Label(
    window,
    text='Buscar elemento por table scan:',
)
table_scan_search.grid(row=5, column=0)
table_scan_search_input = tk.Text(
    window,
    height = 2,
    width = 10,
)
table_scan_search_input.grid(row=5, column=1)

table_scan_search_button = tk.Button(
    window,
    text='Começar Busca por Table Scan',
    command=table_scan_search_fn,
)
table_scan_search_button.grid(row=5, column=2)

## Row 6 ##
table_scan_search_result = tk.Label(window, text='')
table_scan_search_result.grid(row=6, column=0)

## Row 7 ##
index_search = tk.Label(
    window,
    text='Buscar elemento por indice:',
)
index_search.grid(row=7, column=0)
index_search_input = tk.Text(
    window,
    height = 2,
    width = 10,
)
index_search_input.grid(row=7, column=1)

index_search_button = tk.Button(
    window,
    text='Começar Busca por indice',
    command=index_search_fn,
)
index_search_button.grid(row=7, column=2)

## Row 8 ##
index_search_result = tk.Label(window, text='')
index_search_result.grid(row=8, column=0)

window.mainloop()
