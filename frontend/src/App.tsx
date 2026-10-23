import { I18nProvider } from './i18n';
import { NoticeProvider } from './context/NoticeContext';
import { ApplicationLayout } from './components/ApplicationLayout';

export function App() {
  return (
    <I18nProvider>
      <NoticeProvider>
        <ApplicationLayout />
      </NoticeProvider>
    </I18nProvider>
  );
}

export default App;
