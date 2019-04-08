# deoplete-tabnine

A [Deoplete][] source for [TabNine][].

To install on Linux/macOS with vim-plug, first install Deoplete, then add this to your vimrc:

```vim
Plug 'tbodt/deoplete-tabnine', { 'do': './install.sh' }
```

To install on Windows, add this instead:

```vim
Plug 'tbodt/deoplete-tabnine', { 'do': 'powershell.exe .\install.ps1' }
```

  [Deoplete]: https://github.com/Shougo/deoplete.nvim/
  [TabNine]: https://tabnine.com

Configuration:

line_limit
			The buffer update limitation of the current source
			code.
			If the option is smaller, the performance may be
			improved.
			(default: 1000)

max_num_results
       			Max results from TabNine.
			(default: 10)

```vim
call deoplete#custom#var('tabnine', {
\ 'line_limit': 500,
\ 'max_num_results': 20,
\ })
```
