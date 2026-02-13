'use client';

import TabButton from '../atoms/TabButton';
import { TabOption, TabFilter } from '../types';

interface TabBarProps {
  tabs: TabOption[];
  activeTab: TabFilter;
  onTabChange: (tabId: TabFilter) => void;
}

export default function TabBar({ tabs, activeTab, onTabChange }: TabBarProps) {
  return (
    <div className="flex gap-2 overflow-x-auto custom-scrollbar pb-2">
      {tabs.map((tab) => (
        <TabButton
          key={tab.id}
          label={tab.label}
          count={tab.count}
          active={activeTab === tab.id}
          variant={tab.variant}
          onClick={() => onTabChange(tab.id)}
        />
      ))}
    </div>
  );
}
