import PreviewLayout from '@/components/templates/PreviewLayout';
import { mockFileInfo, mockTransactions } from '@/lib/constants';

export default function PreviewPage() {
  return (
    <PreviewLayout
      initialFileInfo={mockFileInfo}
      initialTransactions={mockTransactions}
    />
  );
}
