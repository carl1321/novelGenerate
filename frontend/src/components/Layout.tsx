import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Button, theme } from 'antd';
import {
  HomeOutlined,
  GlobalOutlined,
  UserOutlined,
  BookOutlined,
  BulbOutlined,
  CalendarOutlined,
  PlayCircleOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
  LinkOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/world',
      icon: <GlobalOutlined />,
      label: '1. 世界观生成',
    },
    {
      key: '/character',
      icon: <UserOutlined />,
      label: '2. 角色生成',
    },
    {
      key: '/plot-outline',
      icon: <BookOutlined />,
      label: '3. 剧情大纲',
    },
    {
      key: '/events',
      icon: <CalendarOutlined />,
      label: '4. 事件管理',
    },
    {
      key: '/chapter-outline',
      icon: <BulbOutlined />,
      label: '5. 章节大纲',
    },
    {
      key: '/detailed-plot',
      icon: <PlayCircleOutlined />,
      label: '6. 详细剧情',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{ 
          height: 32, 
          margin: 16, 
          background: 'rgba(255, 255, 255, 0.3)',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold'
        }}>
          {collapsed ? 'NG' : '小说生成'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <AntLayout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '16px',
              width: 64,
              height: 64,
            }}
          />
          <span style={{ 
            fontSize: '18px', 
            fontWeight: 'bold',
            marginLeft: 16 
          }}>
            小说生成智能体框架
          </span>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: 8,
          }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
