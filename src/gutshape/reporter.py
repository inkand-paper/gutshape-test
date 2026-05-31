from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .models import ScanResult, IssueSeverity

console = Console()

class Reporter:
    def print_summary(self, result: ScanResult):
        console.print()
        console.print(Panel.fit(
            f"[bold cyan] GutShape Scan Complete[/bold cyan]\n"
            f"[dim]{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="cyan"
        ))
        
        table = Table(title=" Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Files Scanned", str(result.total_files_scanned))
        table.add_row("Duration", f"{result.scan_duration_ms}ms")
        table.add_row("Issues", str(result.total_issues))
        
        critical_count = sum(1 for i in result.issues if i.severity == IssueSeverity.CRITICAL)
        if critical_count > 0:
            table.add_row(" Critical", f"[red]{critical_count}[/red]")
        
        console.print(table)
        
        if result.issues:
            console.print("\n[bold] Issues:[/bold]\n")
            for issue in result.issues:
                severity_color = "red" if issue.severity == IssueSeverity.CRITICAL else "yellow"
                console.print(f"[{severity_color}][/{severity_color}] {issue.file_path.name}:{issue.line_number}")
                console.print(f"  {issue.description}")
                if issue.suggestion:
                    console.print(f"  [dim] {issue.suggestion}[/dim]")
                console.print()
        else:
            console.print("\n[bold green] No issues found![/bold green]\n")
