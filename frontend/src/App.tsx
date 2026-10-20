import { NoticeProvider } from './context/NoticeContext';
import { ApplicationLayout } from './components/ApplicationLayout';

export function App() {
  return (
    <NoticeProvider>
      <ApplicationLayout />
    </NoticeProvider>
  );
}

export default App;
