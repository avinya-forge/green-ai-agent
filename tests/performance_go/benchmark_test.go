package performance_go

import (
	"go/ast"
	"go/parser"
	"go/token"
	"testing"
)

func BenchmarkGoASTParse(b *testing.B) {
	src := `
package main
import "fmt"
func main() {
	s := ""
	for i := 0; i < 1000; i++ {
		s += "a"
	}
	fmt.Println(s)
}
`
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		fset := token.NewFileSet()
		f, err := parser.ParseFile(fset, "", src, 0)
		if err != nil {
			b.Fatal(err)
		}

		// Simulate visiting the AST
		ast.Inspect(f, func(n ast.Node) bool {
			return true
		})
	}
}
