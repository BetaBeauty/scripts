source $HOME/.vundle.vim

" filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
filetype plugin on

" Switch syntax highlighting on, when the terminal has colors
" Also switch on highlighting the last used search pattern.
if (&t_Co > 2 || has("gui_running"))
   syntax on
   color desert
   " color solarized
   " color molokai
   set hlsearch
   " set incsearch
endif

set laststatus=2
set clipboard=unnamed

"在处理未保存或只读文件的时候,弹出确认
set confirm
"自动换行
set wrap
"整词换行
set linebreak
"Tab键的宽度
set tabstop=2
"统一缩进为4
set softtabstop=2
set shiftwidth=0
set expandtab
"在行和段开始处使用制表符
"set smarttab
"显示行号
set number
"显示行号列号,白色的哪行
set ruler
"突出显示当| wincmd p | diffthis前行
" set cursorline
"ctermbg 代表背景色 cterfg 代表前景色 guibg 下划线的背景色 guifg
"下划线的前景色
"hi CursorLine cterm=NONE ctermbg=darkred ctermfg=white guibg=NONE guifg=NONE
"hi CursorLine cterm=NONE ctermbg=lightgray ctermfg=black guibg=NONE guifg=NONE
"hi CursorLine cterm=NONE ctermbg=lightblue ctermfg=black guibg=NONE guifg=NONE
"hi CursorLine cterm=NONE ctermbg=NONE ctermfg=NONE guibg=lightgray guifg=black
hi VertSplit   term=NONE cterm=NONE
hi StatusLine  term=NONE cterm=NONE
"set cursorcolumn
"用浅色高亮当前行
"autocmd InsertLeave * se nocul
"autocmd InsertLeave * se cul
"历史记录数
set history=1000
"禁止生成临时文件
set nobackup
set noswapfile
"行内替换
"set gdefault
"编码设置
set enc=utf-8
set fencs=utf-8,ucs-bom,shiftjis,gbk
"语言设置
set encoding=utf-8
set langmenu=en_US.UTF-8
language message en_US.UTF-8
" set imcmdline
" source $VIMRUNTIME/delmenu.vim
" source $VIMRUNTIME/menu.vim
"命令行高度,默认为1,这里是1
set cmdheight=1

" Always set autoindenting on
set autoindent
set cindent

"保存全局变量
set viminfo+=!
"带有如下字符的单词不要被换行符分割
set iskeyword+=_,$,@,%,#,-
set linespace=0
"增强命令行自动完成操作
set wildmenu
set backspace=2
set whichwrap+=<,>,h,l
" In many terminal emulators the mouse works just fine, thus enable it.
set mousemodel=popup
set selection=inclusive
set selectmode=mouse,key
"通过使用:command命令,告诉那一行被改动过
"set report=0
"启动时不显示那个援助儿童的提示
set shortmess=atI
"在被分割的窗口显示空白,便于阅读
" set fillchars=vert:\|,stl:^,stlnc:-
"高亮显示匹配的括号
set showmatch
set matchtime=1
"光标移动到buffer顶部和底部时保持3行距离
set scrolloff=3
"自动折叠功能
set foldmethod=indent
set foldlevel=99
map <space> za
"set vim keyword split symbol
set iskeyword=@,48-57,_,192-255

" yank to clipboard
if has("clipboard")
  set clipboard=unnamed " copy to the system clipboard

  if has("unnamedplus") " X11 support
    set clipboard+=unnamedplus
  endif
endif

nnoremap <C-H> <C-W>h
nnoremap <C-J> <C-W>j
nnoremap <C-K> <C-W>k
nnoremap <C-L> <C-W>l

:nnoremap <silent> <Leader>l ml:execute 'match Search /\%'.line('.').'l/'<CR>

nmap <F7> :TlistOpen<CR>
nmap <F8> :TagbarOpen fj<CR>

"只显示当前文件的tags
let Tlist_Enable_Fold_Column = 0
" let Tlist_File_Fold_Auto_Close=1
let Tlist_Show_One_File = 1
"taglist 窗口是最后一个窗口，则退出VIM
let Tlist_Exit_OnlyWindow=1
"在VIM窗口右侧显示taglist窗口
let Tlist_Use_Right_Window=1

let Tlist_GainFocus_On_ToggleOpen=1
let Tlist_Close_On_Select = 1

cabbr <expr> %% expand('%:p:h')
