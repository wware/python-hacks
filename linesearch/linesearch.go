package main

import (
    "bufio"
    "os"
    "fmt"
    "log"
    "regexp"
    "strings"
    "flag"
)


var format = ""
var lines []string


func showLine(n int) {
    formatslice := format[:]
    pattern := regexp.MustCompile(`(%-?[0-9]*[NL])`)
    for {
        result := pattern.FindStringSubmatchIndex(formatslice)
        if len(result) == 0 {
            fmt.Println(formatslice)
            return
        }
        i := result[0]
        j := result[1]
        fmt.Print(formatslice[:i])
        if formatslice[j-1] == 'L' {
            fmt.Print(lines[n])
        } else if formatslice[j-1] == 'N' {
            fmt.Printf(formatslice[i:j-1] + "d", n)
        } else {
            log.Fatalf("huh?", formatslice[i:j])
        }
        formatslice = formatslice[j:]
    }
}

func main() {
    headp := flag.Bool("head", false, "show lines before and including trigger")
    tailp := flag.Bool("tail", false, "show lines after and including trigger")
    regexptr := flag.String("regex", ".*", "regex on which to trigger")
    notp := flag.Bool("not", false, "invert sense of regex, trigger when absent")
    offsetp := flag.Int("offset", 0, "offset for trigger line")
    inputp := flag.String("input", "", "input file")
    formatp := flag.String("format", "%L", "format for how lines are displayed")
    flag.Parse()
    format = *formatp

    var err error
    if *inputp != "" {
        var d []byte
        d, err = os.ReadFile(*inputp)
        lines = strings.Split(string(d), "\n")
        if (len(lines) > 0 && len(lines[len(lines)-1]) == 0) {
            lines = lines[:len(lines)-1]
        }
    } else {
        reader := bufio.NewReader(os.Stdin)
        for {
            line, err := reader.ReadString('\n')
            if err != nil { break }
            line = strings.TrimSuffix(line, "\n")
            lines = append(lines, string(line))
        }
    }
    if err != nil {
        log.Fatal(err)
    }

    var n int = -1
    for i := 0; i < len(lines); i++ {
        matched, err := regexp.MatchString(*regexptr, lines[i])
        if err != nil {
            log.Fatal(err)
        }
        if *notp {
            matched = !matched
        }
        if matched {
            n = i   // zero-indexed
            break
        }
    }
    if n == -1 {
        os.Exit(0)
    }

    n += *offsetp
    if n < 0 {
        n = 0
    } else if n >= len(lines) {
        n = len(lines) - 1
    }

    for i := 0; i < len(lines); i++ {
        if i == n {
            showLine(i)
        } else if (bool(*headp) && i < n) {
            showLine(i)
        } else if (bool(*tailp) && i > n) {
            showLine(i)
        }
    }
}
