package main

import "fmt"

func main() {
    // Excessive logging
    fmt.Println("This is a violation")
    fmt.Printf("Another violation: %s", "hello")

    // Empty block
    if true {
    }

    // Infinite loop
    for {
        // do something
    }
}
