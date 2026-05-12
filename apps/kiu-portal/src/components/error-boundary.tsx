import { Component, type ErrorInfo, type ReactNode } from "react";
import { Button, Card } from "@/components/ui/shared";

type Props = { children: ReactNode };

type State = { hasError: boolean; message?: string };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: undefined };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(_error: Error, _info: ErrorInfo) {
    // Error logging removed for production - could integrate with error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center p-6">
          <Card className="p-8 max-w-md w-full text-center shadow-lg border-destructive/20">
            <h1 className="text-xl font-bold text-primary mb-2">Something went wrong</h1>
            <p className="text-sm text-muted-foreground mb-6">
              {this.state.message || "An unexpected error occurred in the interface."}
            </p>
            <Button type="button" onClick={() => window.location.reload()}>
              Reload page
            </Button>
          </Card>
        </div>
      );
    }
    return this.props.children;
  }
}
