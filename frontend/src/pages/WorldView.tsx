import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Form, message, List, Tag, Space, Progress, Alert, Modal, Drawer, Checkbox } from 'antd';
import { PlusOutlined, SearchOutlined, GlobalOutlined, LoadingOutlined, EditOutlined, DeleteOutlined, EyeOutlined, ThunderboltOutlined } from '@ant-design/icons';

const { TextArea } = Input;


// 格式化力量体系内容
const formatPowerSystemContent = (powerSystem: any) => {
  if (!powerSystem) return "暂无设定";
  
  const realms = powerSystem.cultivation_realms || [];
  
  return (
    <div>
      {realms.length > 0 && (
        <div>
          <h4>修炼境界 (共{realms.length}个)</h4>
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
                  {realm.energy_type && (
                    <div style={{ color: '#1890ff', marginTop: 5 }}>
                      <strong>能量类型:</strong> {realm.energy_type}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {realms.length === 0 && (
        <div style={{ color: '#999' }}>暂无修炼境界数据</div>
      )}
    </div>
  );
};

// 格式化地理设定内容
const formatGeographyContent = (geography: any) => {
  console.log('formatGeographyContent 接收到的数据:', geography);
  if (!geography) {
    console.log('geography 为空，返回暂无设定');
    return "暂无设定";
  }
  
  const regions = geography.main_regions || geography.regions || [];
  const locations = geography.special_locations || [];
  console.log('main_regions 数量:', regions.length, 'special_locations 数量:', locations.length);
  
  // 如果没有任何数据，显示提示
  if (regions.length === 0 && locations.length === 0) {
    return <div style={{ color: '#999' }}>暂无地理设定数据</div>;
  }
  
  return (
    <div>
      {regions.length > 0 && (
        <div>
          <h4>主要区域 (共{regions.length}个)</h4>
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
              <div key={index} style={{ marginBottom: 15, border: '1px solid #e8e8e8', padding: '10px', borderRadius: '4px', backgroundColor: '#fff' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>
                  {region.name || '未命名区域'} 
                  {region.type && <span style={{ fontSize: '14px', color: '#666', marginLeft: '8px' }}>({region.type})</span>}
                </div>
                <div style={{ marginLeft: 10, fontSize: '14px', color: '#666' }}>
                  {region.description && (
                    <div style={{ marginBottom: '8px', lineHeight: '1.6' }}>
                      <strong>描述：</strong>{region.description}
                    </div>
                  )}
                  {region.area_scope && (
                    <div style={{ marginBottom: '4px' }}>
                      <strong>区域范围：</strong>{region.area_scope}
                    </div>
                  )}
                  {region.boundaries && (
                    <div style={{ marginBottom: '4px' }}>
                      <strong>边界：</strong>{region.boundaries}
                    </div>
                  )}
                  {region.resources && region.resources.length > 0 && (
                    <div style={{ marginBottom: '4px' }}>
                      <strong>资源：</strong>{region.resources.join(', ')}
                    </div>
                  )}
                  {region.special_features && (
                    <div style={{ marginBottom: '4px' }}>
                      <strong>特殊特征：</strong>{region.special_features}
                    </div>
                  )}
                  
                  {/* 显示势力分布 */}
                  {region.forces && region.forces.length > 0 && (
                    <div style={{ marginTop: '8px' }}>
                      <div style={{ fontWeight: 'bold', color: '#1890ff', marginBottom: '5px' }}>势力分布:</div>
                      {region.forces.map((force: any, forceIndex: number) => (
                        <div key={forceIndex} style={{ marginLeft: '10px', marginBottom: '8px', padding: '5px', backgroundColor: '#f5f5f5', borderRadius: '3px' }}>
                          <div style={{ fontWeight: 'bold' }}>{force.name}</div>
                          <div style={{ fontSize: '12px', color: '#666' }}>
                            {force.type} | 实力: {force.power_level} | 影响: {force.influence}
                          </div>
                          {force.description && <div style={{ fontSize: '12px', marginTop: '2px' }}>{force.description}</div>}
                          {force.resources_controlled && force.resources_controlled.length > 0 && (
                            <div style={{ fontSize: '12px', marginTop: '2px' }}>
                              控制资源: {force.resources_controlled.join(', ')}
                            </div>
                          )}
                          {force.relationships && (
                            <div style={{ fontSize: '12px', marginTop: '2px' }}>
                              {force.relationships.allies && force.relationships.allies.length > 0 && (
                                <span style={{ color: '#52c41a' }}>盟友: {force.relationships.allies.join(', ')} </span>
                              )}
                              {force.relationships.enemies && force.relationships.enemies.length > 0 && (
                                <span style={{ color: '#ff4d4f' }}>敌人: {force.relationships.enemies.join(', ')} </span>
                              )}
                              {force.relationships.neutral && force.relationships.neutral.length > 0 && (
                                <span style={{ color: '#faad14' }}>中立: {force.relationships.neutral.join(', ')}</span>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
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
                  {location.controlled_by && <div style={{ color: '#1890ff' }}>控制势力: {location.controlled_by}</div>}
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
  const [directEditForm] = Form.useForm();
  const [worldViews, setWorldViews] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(false);
  const [taskStatus, setTaskStatus] = useState<string>('idle');
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  
  // 新增状态
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [selectedWorldView, setSelectedWorldView] = useState<any>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [directEditVisible, setDirectEditVisible] = useState(false);
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState(false);
  const [worldViewToDelete, setWorldViewToDelete] = useState<any>(null);

  // 从数据库获取世界观列表
  const fetchWorldViews = async (keyword?: string) => {
    setListLoading(true);
    try {
      let url = 'http://localhost:8001/api/v1/world/list';
      if (keyword && keyword.trim()) {
        url = `http://localhost:8001/api/v1/world/search?q=${encodeURIComponent(keyword.trim())}`;
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
      const response = await fetch('http://localhost:8001/api/v1/world/create', {
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
      
      // 关闭弹窗
      setCreateModalVisible(false);
      
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
      const response = await fetch(`http://localhost:8001/api/v1/world/${worldView.worldview_id}`);
      if (!response.ok) {
        throw new Error('获取世界观详情失败');
      }
      const detail = await response.json();
      console.log('API返回的详情数据:', detail);
      console.log('geography字段:', detail.geography);
      // 确保字段名一致，将id映射为worldview_id
      const normalizedDetail = {
        ...detail,
        worldview_id: detail.id || detail.worldview_id
      };
      console.log('标准化后的详情数据:', normalizedDetail);
      setSelectedWorldView(normalizedDetail);
      setDetailVisible(true);
    } catch (error: any) {
      message.error(`获取详情失败: ${error.message}`);
    }
  };

  // 进化世界观
  const handleEvolution = async (worldView: any) => {
    try {
      // 先获取完整的世界观数据
      const response = await fetch(`http://localhost:8001/api/v1/world/${worldView.worldview_id}`);
      if (!response.ok) {
        throw new Error('获取世界观详情失败');
      }
      const detail = await response.json();
      
      // 确保字段名一致，将id映射为worldview_id
      const normalizedDetail = {
        ...detail,
        worldview_id: detail.id || detail.worldview_id
      };
      setSelectedWorldView(normalizedDetail);
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

  // 直接编辑世界观
  const handleDirectEdit = async (worldView: any) => {
    try {
      // 先获取完整的世界观数据
      const response = await fetch(`http://localhost:8001/api/v1/world/${worldView.worldview_id}`);
      if (!response.ok) {
        throw new Error('获取世界观详情失败');
      }
      const detail = await response.json();
      console.log('直接编辑 - API返回的详情数据:', detail);
      console.log('直接编辑 - geography字段:', detail.geography);
      
      // 确保字段名一致，将id映射为worldview_id
      const normalizedDetail = {
        ...detail,
        worldview_id: detail.id || detail.worldview_id
      };
      setSelectedWorldView(normalizedDetail);
      
      // 将JSON数据转换为可读的文本格式
      const formatJsonToText = (data: any) => {
        if (!data) return '';
        
        if (typeof data === 'string') return data;
        if (typeof data !== 'object') return String(data);
        
        // 直接返回格式化的JSON字符串，便于编辑
        return JSON.stringify(data, null, 2);
      };
      
      directEditForm.setFieldsValue({
        name: detail.name,
        coreConcept: detail.core_concept,
        description: detail.description,
        power_system: formatJsonToText(detail.power_system),
        geography: formatJsonToText(detail.geography)
      });
      setDirectEditVisible(true);
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
        
        const response = await fetch(`http://localhost:8001/api/v1/world/${selectedWorldView.worldview_id}/partial`, {
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
        const response = await fetch(`http://localhost:8001/api/v1/world/${selectedWorldView.worldview_id}`, {
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
              geography: false
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

  // 保存直接编辑
  const handleSaveDirectEdit = async (values: any) => {
    if (!selectedWorldView) return;
    
    setLoading(true);
    try {
      // 将JSON文本转换回JSON对象
      const parseTextToJson = (text: string, type: 'power_system' | 'geography') => {
        if (!text || text.trim() === '') {
          // 如果文本为空，返回null表示不更新该字段
          console.log(`${type}字段为空，保持现有数据不变`);
          return null;
        }
        
        try {
          // 直接解析JSON格式
          const parsed = JSON.parse(text);
          console.log(`成功解析${type}的JSON数据`);
          return parsed;
        } catch (e) {
          console.warn(`解析${type}的JSON数据失败:`, e);
          // 解析失败时返回null，保持现有数据不变
          return null;
        }
      };
      

      // 构建请求数据，只包含非null的字段
      const requestData: any = {
        name: values.name,
        core_concept: values.coreConcept,
        description: values.description
      };
      
      const powerSystemData = parseTextToJson(values.power_system, 'power_system');
      const geographyData = parseTextToJson(values.geography, 'geography');
      
      if (powerSystemData !== null) {
        requestData.power_system = powerSystemData;
      }
      if (geographyData !== null) {
        requestData.geography = geographyData;
      }
      
      const response = await fetch(`http://localhost:8001/api/v1/world/${selectedWorldView.worldview_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });
      
      if (!response.ok) {
        throw new Error('更新世界观失败');
      }
      
      message.success('世界观编辑成功！');
      setDirectEditVisible(false);
      await fetchWorldViews(); // 刷新列表
    } catch (error: any) {
      message.error(`编辑失败: ${error.message}`);
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
      const response = await fetch(`http://localhost:8001/api/v1/world/${worldViewToDelete.worldview_id}`, {
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
      {/* 世界观创建工作区 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <GlobalOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
          <h3 style={{ marginBottom: 8 }}>世界观生成智能体</h3>
          <p style={{ color: '#666', marginBottom: 24 }}>
            强大的人工智能助手，帮您构建完整的世界观体系
          </p>
          <Button 
            type="primary" 
            size="large"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalVisible(true)}
            style={{ minWidth: 200 }}
          >
            创建新世界观
          </Button>
        </div>
        
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
                  icon={<ThunderboltOutlined />}
                  onClick={() => handleEvolution(item)}
                >
                  进化
                </Button>,
                <Button 
                  type="link" 
                  icon={<EditOutlined />}
                  onClick={() => handleDirectEdit(item)}
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
            <div style={{ marginTop: 20 }}>
              <h3>力量体系</h3>
              <div style={{ background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
                {formatPowerSystemContent(selectedWorldView.power_system)}
              </div>
            </div>
            
            <div style={{ marginTop: 20 }}>
              <h3>地理设定</h3>
              <div style={{ background: '#f5f5f5', padding: 15, borderRadius: 4 }}>
                {(() => {
                  console.log('selectedWorldView.geography:', selectedWorldView.geography);
                  return formatGeographyContent(selectedWorldView.geography);
                })()}
              </div>
            </div>
            
            
          </div>
        )}
      </Drawer>

      {/* 进化模态框 */}
      <Modal
        title="进化世界观"
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

      {/* 直接编辑模态框 */}
      <Modal
        title="编辑世界观"
        open={directEditVisible}
        onCancel={() => setDirectEditVisible(false)}
        footer={null}
        width={800}
      >
        <Form form={directEditForm} onFinish={handleSaveDirectEdit} layout="vertical">
          <Form.Item
            name="name"
            label="世界观名称"
            rules={[{ required: true, message: '请输入世界观名称' }]}
          >
            <Input placeholder="例如：九墟界、洪荒世界等" />
          </Form.Item>
          
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
            name="power_system"
            label="力量体系"
            extra="JSON格式数据，包含cultivation_realms字段，每个境界包含name、level、description、requirements、energy_type字段"
          >
            <TextArea rows={8} placeholder="请输入力量体系的JSON数据..." />
          </Form.Item>
          
          <Form.Item
            name="geography"
            label="地理设定"
            extra="JSON格式数据，包含main_regions、regions、special_locations字段"
          >
            <TextArea rows={8} placeholder="请输入地理设定的JSON数据..." />
          </Form.Item>
          
          
          <Form.Item style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setDirectEditVisible(false)}>
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                icon={<EditOutlined />}
              >
                {loading ? '正在保存...' : '保存修改'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 创建世界观弹窗 */}
      <Modal
        title="创建新世界观"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
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
          
          <Form.Item style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>
                取消
              </Button>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                icon={<PlusOutlined />}
              >
                {loading ? '正在创建...' : '创建世界观'}
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
