set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" Plugin 'chrispoomey/vim-tmux-navigator'
" Plugin 'tmhedberg/SimpylFold'
" Plugin 'vim-scripts/indentpython.vim'

" c++/c
Plugin 'ycm-core/YouCompleteMe'
Plugin 'rdnetto/YCM-Generator'

"Solidity
Plugin 'tomlion/vim-solidity'

" vue
Plugin 'posva/vim-vue'

" golang
" Plugin 'fatih/vim-go', { 'do': ':GoUpdateBinaries' }
Plugin 'ctrlpvim/ctrlp.vim'
" Plugin 'majutsushi/tagbar'

" snipmate for textual snippets
" Plugin 'MarcWeber/vim-addon-mw-utils'
" Plugin 'tomtom/tlib_vim'
" Plugin 'garbas/vim-snipmate'

" Optional
" Plugin 'honza/vim-snippets'
Plugin 'Raimondi/delimitMate'

Plugin 'powerline/powerline', {'rtp': 'powerline/bindings/vim/'}
" Plugin 'kien/ctrlp.vim'

" Plugin 'Lokaltog/powerline', {'rtp': 'powerline/bindings/vim/'}
" wget https://github.com/powerline/powerline/raw/develop/font/PowerlineSymbols.otf
" wget https://github.com/powerline/powerline/raw/develop/font/10-powerline-symbols.conf

" file tree list
Plugin 'scrooloose/nerdtree'
" Plugin 'jistr/vim-nerdtree-tabs'
" Plugin 'Xuyuanp/nerdtree-git-plugin'
Plugin 'scrooloose/nerdcommenter'

" git
" Plugin 'tpope/vim-fugitive'

" python
" Plugin 'scrooloose/syntastic'
" Plugin 'nvie/vim-flake8'

" vim operation
" Plugin 'easymotion/vim-easymotion'

" theme of vim
" Plugin 'altercation/vim-colors-solarized'
" Plugin 'tomasr/molokai'
" Plugin 'jnurmine/Zenburn'

" All of your Plugins must be added before the following line
call vundle#end()            " required

" nerd commenter settings
" Add spaces after comment delimiters by default
let g:NERDSpaceDelims = 1
" Use compact syntax for prettified multi-line comments
let g:NERDCompactSexyComs = 1
" Set a language to use its alternate delimiters by default
let g:NERDAltDelims_java = 1
let g:NERDAltDelims_python = 1
let g:NERDAltDelims_c = 1
" Add your own custom formats or override the defaults
" let g:NERDCustomDelimiters = { 'c': { 'left': '/**','right': '*/' } }
" Enable trimming of trailing whitespace when uncommenting
let g:NERDTrimTrailingWhitespace = 1


" Powerline settings
set t_Co=256

" NerdTree settings
let NERDTreeIgnore=['\.pyc$', '\~$'] "ignore files in NERDTree
map <leader>t :NERDTreeToggle<CR>
let NERDTreeShowHidden=1
autocmd FileChangedShell *.c nested e!
" 在终端启动vim时，共享NERDTree
let g:nerdtree_tabs_open_on_console_startup=1
" 显示书签列表
let NERDTreeShowBookmarks=1
let g:NERDTreeIndicatorMapCustom = {
    \ "Modified"  : "j",
    \ "Staged"    : "✚",
    \ "Untracked" : "✭",
    \ "Renamed"   : "➜",
    \ "Unmerged"  : "═",
    \ "Deleted"   : "✖",
    \ "Dirty"     : "✗",
    \ "Clean"     : "✔︎",
    \ "Unknown"   : "?"
    \ }
nnoremap gb gT
nnoremap gn gt


" YouCompleteMe settings
let g:ycm_global_ycm_extra_conf = '~/.vim/.ycm_extra_conf.py'

" Python environment
let python_highlight_all=1

" let g:ycm_python_binary_path = '/usr/bin/python'
let g:ycm_python_binary_path = 'python'
" set completeopt=longest,menu	"让Vim的补全菜单行为与一般IDE一致(参考VimTip1228)

"youcompleteme  默认tab  s-tab 和自动补全冲突
" let g:ycm_key_list_select_completion = ['<Down>', '<C-N>']
" let g:ycm_key_list_previous_completion = ['<Up>', '<C-P>']
" let g:ycm_key_list_stop_completion = ['<CR>']
let g:ycm_confirm_extra_conf=0 "关闭加载.ycm_extra_conf.py提示
"
let g:ycm_collect_identifiers_from_tags_files=1	" 开启 YCM 基于标签引擎
let g:ycm_min_num_of_chars_for_completion=1	" 从第2个键入字符就开始罗列匹配项
let g:ycm_min_num_identifier_candidate_chars = 1
let g:ycm_cache_omnifunc=0	" 禁止缓存匹配项,每次都重新生成匹配项
let g:ycm_seed_identifiers_with_syntax=1	" 语法关键字补全
" nnoremap <F5> :YcmForceCompileAndDiagnostics<CR>	"force recomile with syntastic
""nnoremap <leader>lo :lopen<CR>	"open locationlist
""nnoremap <leader>lc :lclose<CR>	"close locationlist
"inoremap <leader><leader> <C-x><C-o>
""在注释输入中也能补全
let g:ycm_complete_in_comments = 1
""在字符串输入中也能补全
let g:ycm_complete_in_strings = 1
""注释和字符串中的文字也会被收入补全
let g:ycm_collect_identifiers_from_comments_and_strings = 0

" 补全窗口自动关闭
" let g:ycm_add_preview_to_completeopt = 1
let g:ycm_autoclose_preview_window_after_completion=1

" 跳转到定义处
nnoremap <leader>jd :YcmCompleter GoToDefinitionElseDeclaration<CR> 
map <leader>g  :YcmCompleter GoToDefinitionElseDeclaration<CR>

let g:tagbar_type_go = {
    \ 'ctagstype' : 'go',
    \ 'kinds'     : [
        \ 'p:package',
        \ 'i:imports:1',
        \ 'c:constants',
        \ 'v:variables',
        \ 't:types',
        \ 'n:interfaces',
        \ 'w:fields',
        \ 'e:embedded',
        \ 'm:methods',
        \ 'r:constructor',
        \ 'f:functions'
    \ ],
    \ 'sro' : '.',
    \ 'kind2scope' : {
        \ 't' : 'ctype',
        \ 'n' : 'ntype'
    \ },
    \ 'scope2kind' : {
        \ 'ctype' : 't',
        \ 'ntype' : 'n'
    \ },
    \ 'ctagsbin'  : 'gotags',
    \ 'ctagsargs' : '-sort -silent'
\ }

let g:tagbar_autofocus = 1
" let g:tagbar_autoclose = 1


" delimitMate settings
" for python docstring ", 特别有用
au FileType python let b:delimitMate_nesting_quotes = ['"']
" " 关闭某些类型文件的自动补全
au FileType mail let b:delimitMate_autoclose = 0
"inoremap <C-H> @<Plug>delimitMateS-Tab
"
autocmd FileType vue syntax sync fromstart

