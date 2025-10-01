import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Form, message, List, Tag, Space, Progress, Alert, Modal, Drawer, Checkbox } from 'antd';
import { PlusOutlined, SearchOutlined, GlobalOutlined, LoadingOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';

const { TextArea } = Input;

// 格式化社会组织内容
const formatSocietyContent = (society: any) => {
  if (!society) return "暂无设定";
  
  const organizations = society.organizations || [];
  const socialSystem = society.social_system || {};
  
  return (
    <div>
      {organizations.length > 0 && (
        <div>
          <h4>主要组织</h4>
          {organizations.map((org: any, index: number) => {
            // 处理字符串数组格式
            if (typeof org === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{org}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{org.name}</strong> ({org.type})
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {org.description && <div>描述: {org.description}</div>}
                  {org.power_level && <div>实力等级: {org.power_level}</div>}
                  {org.ideology && <div>理念宗旨: {org.ideology}</div>}
                  {org.structure && <div>组织结构: {org.structure}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {(Object.keys(socialSystem).length > 0 || typeof socialSystem === 'string') && (
        <div style={{ marginTop: 15 }}>
          <h4>社会制度</h4>
          {typeof socialSystem === 'string' ? (
            <div>{socialSystem}</div>
          ) : (
            <div>
              {socialSystem.hierarchy && <div>等级制度: {socialSystem.hierarchy}</div>}
              {socialSystem.economy && <div>经济体系: {socialSystem.economy}</div>}
              {socialSystem.trading && <div>交易方式: {socialSystem.trading}</div>}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// 格式化力量体系内容
const formatPowerSystemContent = (powerSystem: any) => {
  if (!powerSystem) return "暂无设定";
  
  const realms = powerSystem.cultivation_realms || [];
  const energyTypes = powerSystem.energy_types || [];
  const techniques = powerSystem.technique_categories || [];
  
  return (
    <div>
      {realms.length > 0 && (
        <div>
          <h4>修炼境界</h4>
          {realms.map((realm: any, index: number) => {
            // 处理字符串数组格式
            if (typeof realm === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{realm}</strong> (第{index + 1}境)
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{realm.name}</strong> (第{realm.level}境)
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {realm.description && <div>描述: {realm.description}</div>}
                  {realm.requirements && <div>突破要求: {realm.requirements}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {energyTypes.length > 0 && (
        <div style={{ marginTop: 15 }}>
          <h4>能量类型</h4>
          {energyTypes.map((energy: any, index: number) => {
            // 处理字符串数组格式
            if (typeof energy === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{energy}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{energy.name}</strong> ({energy.rarity})
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {energy.description && <div>描述: {energy.description}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {techniques.length > 0 && (
        <div style={{ marginTop: 15 }}>
          <h4>功法分类</h4>
          {techniques.map((technique: any, index: number) => {
            // 处理字符串数组格式
            if (typeof technique === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{technique}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{technique.name}</strong> ({technique.difficulty})
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {technique.description && <div>描述: {technique.description}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// 格式化地理设定内容
const formatGeographyContent = (geography: any) => {
  if (!geography) return "暂无设定";
  
  const regions = geography.main_regions || [];
  const locations = geography.special_locations || [];
  
  return (
    <div>
      {regions.length > 0 && (
        <div>
          <h4>主要区域</h4>
          {regions.map((region: any, index: number) => {
            // 处理字符串数组格式
            if (typeof region === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{region}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{region.name}</strong> ({region.type})
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {region.description && <div>描述: {region.description}</div>}
                  {region.resources && <div>资源: {region.resources.join(', ')}</div>}
                  {region.special_features && <div>特色: {region.special_features}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {locations.length > 0 && (
        <div style={{ marginTop: 15 }}>
          <h4>特殊地点</h4>
          {locations.map((location: any, index: number) => {
            // 处理字符串数组格式
            if (typeof location === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{location}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{location.name}</strong> ({location.type})
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {location.description && <div>描述: {location.description}</div>}
                  {location.significance && <div>重要性: {location.significance}</div>}
                  {location.dangers && <div>危险: {location.dangers.join(', ')}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// 格式化历史文化内容
const formatHistoryContent = (history: any) => {
  if (!history) return "暂无设定";
  
  const events = history.historical_events || [];
  const features = history.cultural_features || [];
  const conflicts = history.current_conflicts || [];
  
  return (
    <div>
      {events.length > 0 && (
        <div>
          <h4>历史事件</h4>
          {events.map((event: any, index: number) => {
            // 处理字符串数组格式
            if (typeof event === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{event}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{event.name}</strong> ({event.time_period})
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {event.description && <div>描述: {event.description}</div>}
                  {event.impact && <div>影响: {event.impact}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {features.length > 0 && (
        <div style={{ marginTop: 15 }}>
          <h4>文化特色</h4>
          {features.map((feature: any, index: number) => {
            // 处理字符串数组格式
            if (typeof feature === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{feature}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{feature.region}</strong>
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {feature.traditions && <div>传统习俗: {feature.traditions}</div>}
                  {feature.values && <div>价值观念: {feature.values}</div>}
                  {feature.lifestyle && <div>生活方式: {feature.lifestyle}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {conflicts.length > 0 && (
        <div style={{ marginTop: 15 }}>
          <h4>当前冲突</h4>
          {conflicts.map((conflict: any, index: number) => {
            // 处理字符串数组格式
            if (typeof conflict === 'string') {
              return (
                <div key={index} style={{ marginBottom: 10 }}>
                  <strong>{conflict}</strong>
                </div>
              );
            }
            // 处理对象格式
            return (
              <div key={index} style={{ marginBottom: 10 }}>
                <strong>{conflict.name}</strong>
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {conflict.description && <div>描述: {conflict.description}</div>}
                  {conflict.parties && <div>参与方: {conflict.parties.join(', ')}</div>}
                  {conflict.stakes && <div>利害关系: {conflict.stakes}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

const WorldView: React.FC = () => {
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const [worldViews, setWorldViews] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(false);
  const [taskStatus, setTaskStatus] = useState<string>('idle');
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  
  // 新增状态
  const [selectedWorldView, setSelectedWorldView] = useState<any>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState(false);
  const [worldViewToDelete, setWorldViewToDelete] = useState<any>(null);

  // 从数据库获取世界观列表
  const fetchWorldViews = async (keyword?: string) => {
    setListLoading(true);
    try {
      let url = 'http://localhost:8000/api/v1/world/list';
      if (keyword && keyword.trim()) {
        url = `http://localhost:8000/api/v1/world/search?q=${encodeURIComponent(keyword.trim())}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('获取世界观列表失败');
      }
      
      const data = await response.json();
      console.log('世界观API响应数据:', data);
      
      // 根据API响应结构设置数据
      if (Array.isArray(data)) {
        console.log('数据是数组格式，直接设置');
        setWorldViews(data);
      } else if (data.worldviews && Array.isArray(data.worldviews)) {
        console.log('数据包含worldviews字段，设置worldviews数组');
        setWorldViews(data.worldviews);
      } else {
        console.warn('意外的数据格式:', data);
        setWorldViews([]);
      }
    } catch (error: any) {
      message.error(`获取世界观列表失败: ${error.message}`);
      console.error('获取世界观列表失败:', error);
    } finally {
      setListLoading(false);
    }
  };

  // 组件加载时获取世界观列表
  useEffect(() => {
    fetchWorldViews();
  }, []);


  const handleCreateWorldView = async (values: any) => {
    setLoading(true);
    setTaskStatus('processing');
    try {
      const response = await fetch('http://localhost:8000/api/v1/world/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          core_concept: values.coreConcept,
          description: values.description,
          additional_requirements: values.updateRequirements ? { "requirements": values.updateRequirements } : {}
        }),
      });

      if (!response.ok) {
        throw new Error('世界观创建失败');
      }

      const worldView = await response.json();
      message.success('世界观创建成功！');
      form.resetFields();
      
      // 刷新世界观列表
      await fetchWorldViews();
      setTaskStatus('completed');
      
      // 生成MD内容用于显示
      if (worldView) {
      }
      
    } catch (error: any) {
      message.error(`生成失败: ${error.message}`);
      setTaskStatus('failed');
    } finally {
      setLoading(false);
    }
  };

  // 查看详情
  const handleViewDetail = async (worldView: any) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/world/${worldView.worldview_id}`);
      if (!response.ok) {
        throw new Error('获取世界观详情失败');
      }
      const detail = await response.json();
      setSelectedWorldView(detail);
      setDetailVisible(true);
    } catch (error: any) {
      message.error(`获取详情失败: ${error.message}`);
    }
  };

  // 编辑世界观
  const handleEdit = async (worldView: any) => {
    try {
      // 先获取完整的世界观数据
      const response = await fetch(`http://localhost:8000/api/v1/world/${worldView.worldview_id}`);
      if (!response.ok) {
        throw new Error('获取世界观详情失败');
      }
      const detail = await response.json();
      
      setSelectedWorldView(detail);
      editForm.setFieldsValue({
        coreConcept: detail.core_concept,
        description: detail.description,
        updateRequirements: '',
        updateOptions: [] // Checkbox.Group 期望的是数组，不是对象
      });
      setEditVisible(true);
    } catch (error: any) {
      message.error(`获取世界观详情失败: ${error.message}`);
    }
  };

  // 保存编辑
  const handleSaveEdit = async (values: any) => {
    if (!selectedWorldView) return;
    
    setLoading(true);
    try {
      // 检查是否有选择更新维度
      const hasDimensionUpdate = values.updateOptions && values.updateOptions.length > 0;
      
      if (hasDimensionUpdate) {
        // 使用部分更新接口
        const updateDimensions = values.updateOptions; // 直接使用数组
        
        const response = await fetch(`http://localhost:8000/api/v1/world/${selectedWorldView.worldview_id}/partial`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            core_concept: values.coreConcept,
            description: values.description,
            update_dimensions: updateDimensions,
            update_description: values.updateRequirements || '更新选中的维度'
          }),
        });
        
        if (!response.ok) {
          throw new Error('部分更新失败');
        }
        
        message.success(`世界观部分更新成功！更新了 ${updateDimensions.length} 个维度`);
      } else {
        // 只更新基本信息，使用原来的接口
        const response = await fetch(`http://localhost:8000/api/v1/world/${selectedWorldView.worldview_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            core_concept: values.coreConcept,
            description: values.description,
            additional_requirements: values.updateRequirements ? { "requirements": values.updateRequirements } : {},
            update_options: {
              power_system: false,
              geography: false,
              culture: false,
              history: false
            }
          }),
        });
        
        if (!response.ok) {
          throw new Error('更新世界观失败');
        }
        
        message.success('世界观基本信息更新成功！');
      }
      
      setEditVisible(false);
      await fetchWorldViews(); // 刷新列表
    } catch (error: any) {
      message.error(`更新失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 删除世界观
  const handleDelete = (worldView: any) => {
    setWorldViewToDelete(worldView);
    setDeleteConfirmVisible(true);
  };

  // 确认删除
  const handleConfirmDelete = async () => {
    if (!worldViewToDelete) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/world/${worldViewToDelete.worldview_id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('删除世界观失败');
      }

      message.success('世界观删除成功！');
      setDeleteConfirmVisible(false);
      await fetchWorldViews(); // 刷新列表
    } catch (error: any) {
      message.error(`删除失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="1. 世界观生成" style={{ marginBottom: 16 }}>
        <Form form={form} onFinish={handleCreateWorldView} layout="vertical">
          <Form.Item
            name="coreConcept"
            label="核心概念"
            rules={[{ required: true, message: '请输入核心概念' }]}
          >
            <Input placeholder="例如：洪荒修仙、克苏鲁修仙等" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="详细描述"
            rules={[{ required: true, message: '请输入详细描述' }]}
          >
            <TextArea rows={4} placeholder="描述你的世界观设定..." />
          </Form.Item>
          
          <Form.Item
            name="updateRequirements"
            label="特殊要求"
          >
            <TextArea rows={3} placeholder="可选：特殊要求、风格偏好、限制条件等..." />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} icon={<PlusOutlined />}>
              {loading ? '正在创建...' : '创建世界观'}
            </Button>
          </Form.Item>
        </Form>
        
        {/* 任务状态显示 */}
        {taskStatus === 'processing' && (
          <Alert
            message="世界观构建中"
            description={
              <div>
                <p>创建成功，请耐心等待世界观构建完成。</p>
                <Progress 
                  percent={30} 
                  status="active" 
                  strokeColor="#1890ff"
                  format={() => (
                    <Space>
                      <LoadingOutlined />
                      <span>构建中...</span>
                    </Space>
                  )}
                />
              </div>
            }
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
        
        {taskStatus === 'queued' && (
          <Alert
            message="任务已加入队列"
            description="世界观生成任务已加入处理队列，请耐心等待。"
            type="info"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
        
        {taskStatus === 'completed' && (
          <Alert
            message="世界观构建完成"
            description="世界观已成功构建完成，请查看下方结果。"
            type="success"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
        
        {taskStatus === 'failed' && (
          <Alert
            message="世界观构建失败"
            description="构建过程中出现错误，请重试。"
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}
      </Card>


      <Card 
        title="世界观列表" 
        extra={
          <Space>
            <Input.Search
              placeholder="搜索世界观..."
              value={searchKeyword}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchKeyword(e.target.value)}
              onSearch={fetchWorldViews}
              style={{ width: 200 }}
            />
            <Button 
              icon={<SearchOutlined />}
              onClick={() => fetchWorldViews(searchKeyword)}
              loading={listLoading}
            >
              搜索
            </Button>
          </Space>
        }
      >
        <List
          loading={listLoading}
          dataSource={worldViews || []}
          renderItem={(item: any, index: number) => {
            console.log('渲染世界观项目:', item, '索引:', index);
            return (
            <List.Item
              actions={[
                <Button 
                  type="link" 
                  icon={<EyeOutlined />}
                  onClick={() => handleViewDetail(item)}
                >
                  查看详情
                </Button>,
                <Button 
                  type="link" 
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(item)}
                >
                  编辑
                </Button>,
                <Button 
                  type="link" 
                  danger 
                  icon={<DeleteOutlined />}
                  onClick={() => handleDelete(item)}
                >
                  删除
                </Button>,
              ]}
            >
              <List.Item.Meta
                avatar={<GlobalOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                title={
                  <Space>
                    {item.name || '未命名世界观'}
                    {index === worldViews.length - 1 && <Tag color="green">最新</Tag>}
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small">
                    <div>{item.description || '暂无描述'}</div>
                    <Space>
                      <Tag color="blue">修仙</Tag>
                      <Tag color="green">世界观</Tag>
                      <Tag color="orange">
                        {item.created_at ? new Date(item.created_at).toLocaleDateString() : '未知日期'}
                      </Tag>
                    </Space>
                  </Space>
                }
              />
            </List.Item>
            );
          }}
        />
      </Card>

      {/* 详情抽屉 */}
      <Drawer
        title="世界观详情"
        placement="right"
        width={800}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
      >
        {selectedWorldView && (
          <div>
            <h2>{selectedWorldView.name}</h2>
            <p><strong>核心概念:</strong> {selectedWorldView.core_concept}</p>
            <p><strong>描述:</strong> {selectedWorldView.description}</p>
            <p><strong>创建时间:</strong> {new Date(selectedWorldView.created_at).toLocaleString()}</p>
            <p><strong>更新时间:</strong> {new Date(selectedWorldView.updated_at).toLocaleString()}</p>
            
            {/* 显示5维度内容 */}
            {selectedWorldView.power_system && (
              <div style={{ marginTop: 20 }}>
                <h3>力量体系</h3>
                <div style={{ background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
                  {formatPowerSystemContent(selectedWorldView.power_system)}
                </div>
              </div>
            )}
            
            {selectedWorldView.geography && (
              <div style={{ marginTop: 20 }}>
                <h3>地理设定</h3>
                <div style={{ background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
                  {formatGeographyContent(selectedWorldView.geography)}
                </div>
              </div>
            )}
            
            {selectedWorldView.culture && (
              <div style={{ marginTop: 20 }}>
                <h3>社会组织</h3>
                <div style={{ background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
                  {formatSocietyContent(selectedWorldView.culture)}
                </div>
              </div>
            )}
            
            {selectedWorldView.history && (
              <div style={{ marginTop: 20 }}>
                <h3>历史文化</h3>
                <div style={{ background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
                  {formatHistoryContent(selectedWorldView.history)}
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>

      {/* 编辑模态框 */}
      <Modal
        title="编辑世界观"
        open={editVisible}
        onCancel={() => setEditVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={editForm} onFinish={handleSaveEdit} layout="vertical">
          <Form.Item
            name="coreConcept"
            label="核心概念"
            rules={[{ required: true, message: '请输入核心概念' }]}
          >
            <Input placeholder="例如：洪荒修仙、克苏鲁修仙等" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="详细描述"
            rules={[{ required: true, message: '请输入详细描述' }]}
          >
            <TextArea rows={4} placeholder="描述你的世界观设定..." />
          </Form.Item>
          
          <Form.Item
            name="updateRequirements"
            label="更新要求"
            extra="描述你想要如何更新选中的维度"
          >
            <TextArea rows={3} placeholder="例如：增加2个新的修炼境界、添加更多地理区域等..." />
          </Form.Item>
          
          <Form.Item
            name="updateOptions"
            label="更新选项"
            extra="选择要重新生成的维度，未选择的维度将保留原有内容"
          >
            <Checkbox.Group>
              <Space direction="vertical">
                <Checkbox value="power_system">力量体系</Checkbox>
                <Checkbox value="geography">地理设定</Checkbox>
                <Checkbox value="culture">社会组织</Checkbox>
                <Checkbox value="history">历史文化</Checkbox>
              </Space>
            </Checkbox.Group>
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={loading}>
                保存修改
              </Button>
              <Button onClick={() => setEditVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 删除确认模态框 */}
      <Modal
        title="确认删除"
        open={deleteConfirmVisible}
        onOk={handleConfirmDelete}
        onCancel={() => setDeleteConfirmVisible(false)}
        confirmLoading={loading}
        okText="确认删除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <p>确定要删除世界观 <strong>{worldViewToDelete?.name}</strong> 吗？</p>
        <p style={{ color: '#ff4d4f' }}>此操作不可撤销！</p>
      </Modal>
    </div>
  );
};

export default WorldView;
