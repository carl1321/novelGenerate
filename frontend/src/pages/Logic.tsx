import React, { useState } from 'react';
import { Card, Button, List, Tag, Space, Alert, Progress } from 'antd';
import { BulbOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';

const Logic: React.FC = () => {
  const [logicChecks, setLogicChecks] = useState([
    {
      id: 1,
      title: '角色行为一致性检查',
      status: '通过',
      score: 85,
      issues: [],
    },
    {
      id: 2,
      title: '修炼体系逻辑检查',
      status: '警告',
      score: 72,
      issues: ['境界提升过快', '功法使用不合理'],
    },
    {
      id: 3,
      title: '时间线一致性检查',
      status: '通过',
      score: 90,
      issues: [],
    },
    {
      id: 4,
      title: '世界观一致性检查',
      status: '错误',
      score: 45,
      issues: ['地理设定矛盾', '组织关系错误'],
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case '通过': return 'success';
      case '警告': return 'warning';
      case '错误': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case '通过': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case '警告': return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      case '错误': return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default: return null;
    }
  };

  return (
    <div>
      <Card title="逻辑反思引擎" style={{ marginBottom: 16 }}>
        <Alert
          message="逻辑反思引擎正在运行"
          description="系统会自动检查内容的逻辑一致性，发现问题时会及时提醒并提供修改建议。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<BulbOutlined />}>
            开始检查
          </Button>
          <Button>生成报告</Button>
          <Button>导出结果</Button>
        </Space>
      </Card>

      <Card title="检查结果">
        <List
          dataSource={logicChecks}
          renderItem={(item) => (
            <List.Item>
              <Card size="small" style={{ width: '100%' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                      {getStatusIcon(item.status)}
                      <span style={{ marginLeft: 8, fontWeight: 'bold' }}>{item.title}</span>
                      <Tag color={getStatusColor(item.status)} style={{ marginLeft: 8 }}>
                        {item.status}
                      </Tag>
                    </div>
                    
                    {item.issues.length > 0 && (
                      <div style={{ marginTop: 8 }}>
                        <div style={{ color: '#666', marginBottom: 4 }}>发现的问题：</div>
                        <Space wrap>
                          {item.issues.map((issue, index) => (
                            <Tag key={index} color="red">{issue}</Tag>
                          ))}
                        </Space>
                      </div>
                    )}
                  </div>
                  
                  <div style={{ width: 200, marginLeft: 16 }}>
                    <div style={{ textAlign: 'center', marginBottom: 8 }}>
                      <span style={{ fontSize: 18, fontWeight: 'bold' }}>{item.score}</span>
                      <span style={{ color: '#666', marginLeft: 4 }}>分</span>
                    </div>
                    <Progress 
                      percent={item.score} 
                      size="small" 
                      strokeColor={item.score >= 80 ? '#52c41a' : item.score >= 60 ? '#faad14' : '#ff4d4f'}
                    />
                  </div>
                </div>
              </Card>
            </List.Item>
          )}
        />
      </Card>

      <Card title="总体评估" style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-around' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>73</div>
            <div>平均分</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>2</div>
            <div>通过检查</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>1</div>
            <div>需要警告</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 24, fontWeight: 'bold', color: '#ff4d4f' }}>1</div>
            <div>需要修复</div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Logic;
