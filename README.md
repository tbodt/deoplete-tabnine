# deoplete-tabnine


## Overview

A [Deoplete][] source for [TabNine][].


## Installation

To install it with vim-plug, first install Deoplete, then add this to your vimrc:

```vim
if has('win32') || has('win64')
  Plug 'tbodt/deoplete-tabnine', { 'do': 'powershell.exe .\install.ps1' }
else
  Plug 'tbodt/deoplete-tabnine', { 'do': './install.sh' }
endif
```

For [dein.vim](https://github.com/Shougo/dein.vim)

```vim
if has('win32') || has('win64')
  call dein#add('tbodt/deoplete-tabnine', { 'build': 'powershell.exe .\install.ps1' })
else
  call dein#add('tbodt/deoplete-tabnine', { 'build': './install.sh' })
endif
```

[Deoplete]: https://github.com/Shougo/deoplete.nvim/
[TabNine]: https://tabnine.com


## Configuration

### `line_limit`

The number of lines before and after the cursor to send to TabNine. If the
option is smaller, the performance may be improved.  (default: 1000)


### `max_num_results`

Max results from TabNine.
(default: 10)

```vim
call deoplete#custom#var('tabnine', {
\ 'line_limit': 500,
\ 'max_num_results': 20,
\ })
```
