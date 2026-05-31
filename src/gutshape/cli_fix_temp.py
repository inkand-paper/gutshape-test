@app.command()
def fix(path: Path = typer.Argument(Path.cwd(), help="Path to scan")):
    """Auto-fix security issues (dry run by default)"""
    from .auto_fixer import AutoFixer
    console.print("[bold cyan] Auto-Fixer[/bold cyan]\n")
    console.print("[yellow] DRY RUN MODE - No changes will be made[/yellow]")
    console.print("[dim]To actually fix the files, run: gutshape apply[/dim]\n")
    scanner = CodeScanner(str(path))
    result = scanner.scan()
    if result.total_issues == 0:
        console.print("[green] No issues found![/green]")
        return
    console.print(f"Found [yellow]{result.total_issues}[/yellow] issues\n")
    fixer = AutoFixer(dry_run=True)
    fixes = fixer.apply_fixes(result.issues, dry_run=True)
    if fixes:
        console.print("[bold]Would apply these fixes:[/bold]\n")
        for fix_item in fixes:
            console.print(f"  [yellow] Would fix:[/yellow] {fix_item['issue']}")
        console.print("\n[bold green]To apply fixes, run:[/bold green]")
        console.print(f"  gutshape apply")
    else:
        console.print("[yellow]No automatic fixes available[/yellow]")
