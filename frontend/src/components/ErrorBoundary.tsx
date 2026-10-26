import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertOctagon, RotateCw, Home } from 'lucide-react';
import { useTranslation } from '../i18n';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

const ErrorFallbackView: React.FC<{
  error: Error | null;
  onReset: () => void;
}> = ({ error, onReset }) => {
  const { t } = useTranslation();

  return (
    <div className="min-h-[400px] flex items-center justify-center p-6 w-full">
      <div className="max-w-lg w-full bg-white border border-red-200 rounded-2xl p-6 shadow-xl text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center text-red-600 mx-auto">
          <AlertOctagon className="w-6 h-6" />
        </div>

        <div className="space-y-1">
          <h2 className="text-base font-bold text-[#12233D]">
            {t('errorBoundaryTitle')}
          </h2>
          <p className="text-xs text-[#526176] leading-relaxed">
            {t('errorBoundaryDesc')}
          </p>
        </div>

        {error && (
          <div className="text-left bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs font-mono text-red-700 max-h-36 overflow-y-auto">
            <span className="font-bold block mb-1">Diagnostic Details:</span>
            {error.toString()}
          </div>
        )}

        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-[#08785D] hover:bg-[#06664E] shadow-xs cursor-pointer transition-all"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>{t('errorBoundaryReload')}</span>
          </button>
          <button
            type="button"
            onClick={() => {
              onReset();
              if (typeof window !== 'undefined') {
                window.location.hash = '';
                window.location.reload();
              }
            }}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-[#526176] bg-slate-100 hover:bg-slate-200 hover:text-[#12233D] transition cursor-pointer"
          >
            <Home className="w-3.5 h-3.5" />
            <span>Reload Page</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    console.error('ErrorBoundary caught an unhandled render error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorFallbackView
          error={this.state.error}
          onReset={this.handleReset}
        />
      );
    }

    return this.props.children;
  }
}
