# Slides For The Sept 28, 2026, `/dev/reno` Presentation

## Slide One

```text
 ╠══[ Calling Go From Python ]════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 

                      _=gj88888888lkoz=,_                                                                                 Sean Jain Ellis
                    D888888888888888888888b,                                                                           bandarji.github.io
                  j88P""V8888888888888888888                                                                          github.com/bandarji
                  888    8888888888888888888
                  888baed8888888888888888888
                                8888888888888
        ,ad8888888888888888888888888888888888  888888be,
      d8888888888888888888888888888888888888  888888888b,
      d88888888888888888888888888888888888888  8888888888b,
    j888888888888888888888888888888888888888  88888888888p,
    j888888888888888888888888888888888888888'  8888888888888
    8888888888888888888888888888888888888^"   ,8888888888888
    88888888888888^'                        .d88888888888888
    8888888888888"   .a8888888888888888888888888888888888888
    8888888888888  ,888888888888888888888888888888888888888^                      ,_---~~~~~----._         
    ^888888888888  888888888888888888888888888888888888888^                _,,_,*^____      _____``*g*\"*, 
    V88888888888  88888888888888888888888888888888888888Y                / __/ /'     ^.  /      \  @    | 
      V8888888888  88888888888888888888888888888888888^"'                [  @  | @))    |  | @))   l  @ _/  
      ´"^8888888  8888888888888                                          \`/   \~____ / __ \_____/    \   
                  8888888888888888888888888                               |           _l__l_           ]   
                  8888888888888888888P""V88                               |          [______]           ]  
                  8888888888888888888    88                               |            | | |            |  
                  8888888888888888888baed88                               l            '- -'            |  
                    ´^88888888888888888888^                                |                            |   
                      ´'"^=V888888888V=^'´                                  |                           |   


                                                                                                         
 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Two

```text
 ╠══[ Calling Go From Python :: Compile A Shared Library ]════════════════════════════════════════════════════════════════════════════════╣


                      _=gj88888888lkoz=,_
                    D888888888888888888888b,                                                  ##########
                  j88P""V8888888888888888888                                                ##############
                  888    8888888888888888888                                               ####        ####
                  888baed8888888888888888888                                              ####
                                8888888888888                                             ####
        ,ad8888888888888888888888888888888888  888888be,                                  ####
      d8888888888888888888888888888888888888  888888888b,                                 ####
      d88888888888888888888888888888888888888  8888888888b,                                ####        ####
    j888888888888888888888888888888888888888  88888888888p,                                 ##############
    j888888888888888888888888888888888888888'  8888888888888                                  ##########
    8888888888888888888888888888888888888^"   ,8888888888888
    88888888888888^'                        .d88888888888888
    8888888888888"   .a8888888888888888888888888888888888888
    8888888888888  ,888888888888888888888888888888888888888^                      ,_---~~~~~----._         
    ^888888888888  888888888888888888888888888888888888888^                _,,_,*^____      _____``*g*\"*, 
    V88888888888  88888888888888888888888888888888888888Y                / __/ /'     ^.  /      \ ^@q   f 
      V8888888888  88888888888888888888888888888888888^"'                [  @f | @))    |  | @))   l  0 _/  
      ´"^8888888  8888888888888                                          \`/   \~____ / __ \_____/    \   
                  8888888888888888888888888                               |           _l__l_           I   
                  8888888888888888888P""V88                               }          [______]           I  
                  8888888888888888888    88                               ]            | | |            |  
                  8888888888888888888baed88                               ]             ~ ~             |  
                    ´^88888888888888888888^                                |                            |   
                      ´'"^=V888888888V=^'´                                  |                           |   



 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Three

```text
 ╠══[ Calling Go From Python :: Howto With Go And Python ]════════════════════════════════════════════════════════════════════════════════╣

   ╔════════════╗
   ║  Go (CGO)  ║
   ╚════════════╝

     Add any amount of C code as a comment block before the
     import of Go's C package.

       // #include <stdio.h>
       // #include <errno.h>
       import "C"
       import "unsafe" // needed for void pointer support

     Compile as a shared library.

       go build -buildmode=c-shared -o <name>.(so|dylib|dll) .

   ╔═══════════════════╗
   ║  Python (ctypes)  ║
   ╚═══════════════════╝

       import ctypes
       lib = ctypes.CDLL("./my_lib.so")
       lib.FunctionToCall(p1, p2, p3)






 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Four

```text
 ╠══[ Calling Go From Python :: Supported Data Types ]════════════════════════════════════════════════════════════════════════════════════╣

      ╔═════════════════════════╦═════════════════════════════════╦══════════════════════════════════╗
      ║ Python Type             ║ Go Type                         ║ CGO Type                         ║
      ╠═════════════════════════╬═════════════════════════════════╬══════════════════════════════════╣
      ║ None                    ║ nil / unsafe.Pointer            ║ void*                            ║
      ║ bool                    ║ bool                            ║ GoUint8                          ║
      ║ int                     ║ int8-int64, uint8-uint64        ║ GoInt8-GoInt64, GoUint8-GoUint64 ║
      ║ float                   ║ float32, float64                ║ GoFloat32, GoFloat64             ║
      ║ complex                 ║ C.CPyComplex64, C.CPyComplex128 ║ CPyComplex64, CPyComplex128      ║
      ║ str                     ║ string                          ║ char*                            ║
      ║ bytes                   ║ []byte                          ║ char*, int*                      ║
      ╠═════════════════════════╬═════════════════════════════════╬══════════════════════════════════╣
      ║ Record (NamedTuple)     ║ Record                          ║ CRecord                          ║
      ║ count: int              ║ Count: int64                    ║ count: int64_t                   ║
      ║ ratio: float            ║ Ratio: float64                  ║ ratio: double                    ║
      ║ ready: bool             ║ Ready: bool                     ║ ready: unsigned char             ║
      ╚═════════════════════════╩═════════════════════════════════╩══════════════════════════════════╝

      Pointers?

        Go's garbage collector cannot track pointers passed to C. If needed,
        an option exists. Use gopy to compile a Cython extension module from a
        Go package. This implementation replaces pointers with int64 handlers.
        This keeps Go's garbage collection from reclaiming memory.
  
        




 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Five

```text
 ╠══[ Calling Go From Python :: CGO vs gopy ]═════════════════════════════════════════════════════════════════════════════════════════════╣

      ╔═════════════════╦══════════════════════════════╦══════════════════════════════════╗
      ║ Component       ║ CGO                          ║ gopy                             ║
      ╠═════════════════╬══════════════════════════════╬══════════════════════════════════╣
      ║ Compatibility   ║ Standard library             ║ Installed 3rd party tool         ║
      ║ Python access   ║ Shared library with ctypes   ║ Extension module called          ║
      ║ Strings         ║ C.CString                    ║ Converted to str                 ║
      ║ Structs         ║ Copied through a C struct    ║ Python class, fields and methods ║
      ║ Slices and maps ║ No C equivalent              ║ Generates wrappers               ║
      ║ Objects         ║ C values and pointers        ║ Uses int64 in place of pointers  ║
      ║ Build           ║ Uses Go to build shared lib  ║ Uses gopy to build               ║
      ╚═════════════════╩══════════════════════════════╩══════════════════════════════════╝

        Ask your doctor if SharedLib(tm) is right for you. Just because you
        can does not mean you should. Though, writing a bunch of code in Go,
        then importing that one repository into several languages has some
        appeal.













 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Six

```text
 ╠══[ Calling Go From Python :: Global Interpreter Lock ]═════════════════════════════════════════════════════════════════════════════════╣

      Global Interpreter Lock?

        Python releases the GIL when calling a Go function. Python threads will
        truly execute concurrently. GIL sits idly in the interpreter, waiting for
        threads to return.

        At the Python level, thread_a and thread_b can spin up and execute
        concurrently. In the Go function, goroutines can also spin up, where
        the Go scheduler takes control. The scheduler distributes goroutines
        across its OS threads pool (GOMAXPROCS for maximum OS thread count).

      OS Threads Versus Coroutines

        Every Python thread that calls a Go function assigns an OS thread for
        tracking. Go will keep track of threads on a 1:1 basis with Python
        threads, in addition to its own pool. OS threads, heavier than goroutines,
        will increase memory overhead.

        Opinion: Use zero or one Python threads to call Go. Let Go spin up
        goroutines for concurrency.









 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Seven

```text
 ╠══[ Calling Go From Python :: Supporting Data Types ]═══════════════════════════════════════════════════════════════════════════════════╣

      What if...?

      What if Python sends unexpected arguments to a Go function?                 

        import ctypes
        lib = ctypes.CDLL("./my_lib.so")
        lib.FunctionToCall.argtypes = [ctypes.c_int]  # <-- important
        lib.FunctionToCall("hello")

        Execution stops. No data gets sent to C or Go functions.
        Python raises a TypeError exception.

      What if the Python code does not contain the argtypes information?

        ╔═════════════════════╦═════════════════════════════════╗
        ║ Lucky               ║ Unlucky                         ║
        ╠═════════════════════╬═════════════════════════════════╣
        ║ Bad Processing      ║ Go panic                        ║
        ║ Unexpected Output   ║ Segmentation fault (SIGSEGV)    ║
        ║                     ║ Annihilation of the multiverse! ║
        ╚═════════════════════╩═════════════════════════════════╝



                                                          GET YOUR PHONES READY !!!




 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```

## Slide Eight

```text
 ╠══[ Calling Go From Python :: Thank You ]═══════════════════════════════════════════════════════════════════════════════════════════════╣
 

                      _=gj88888888lkoz=,_
                    D888888888888888888888b,                                                          [QR Code To Code Repository Here]                                      
                  j88P""V8888888888888888888
                  888    8888888888888888888
                  888baed8888888888888888888
                                8888888888888
        ,ad8888888888888888888888888888888888  888888be,
      d8888888888888888888888888888888888888  888888888b,
      d88888888888888888888888888888888888888  8888888888b,
    j888888888888888888888888888888888888888  88888888888p,
    j888888888888888888888888888888888888888'  8888888888888
    8888888888888888888888888888888888888^"   ,8888888888888
    88888888888888^'                        .d88888888888888
    8888888888888"   .a8888888888888888888888888888888888888
    8888888888888  ,888888888888888888888888888888888888888^                      ,_---~~~~~----._         
    ^888888888888  888888888888888888888888888888888888888^                _,,_,*^____      _____``*g*\"*, 
    V88888888888  88888888888888888888888888888888888888Y                / __/ /'     ^.  /      \  @    | 
      V8888888888  88888888888888888888888888888888888^"'                [  @  | @))    |  | @))   l  @ _/  
      ´"^8888888  8888888888888                                          \`/   \~____ / __ \_____/    \   
                  8888888888888888888888888                               |           _l__l_           ]   
                  8888888888888888888P""V88                               |          [______]           ]               Sean Jain Ellis
                  8888888888888888888    88                               |            | | |            |            bandarji.github.io
                  8888888888888888888baed88                               l            '- -'            |           github.com/bandarji
                    ´^88888888888888888888^                                |                            |   
                      ´'"^=V888888888V=^'´                                  |                           |   


                                                                                                         
 ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
```
