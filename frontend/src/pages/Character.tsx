import React, { useState, useEffect } from 'react';
import { Card, Button, Table, Tag, Space, Modal, Form, Input, Select, InputNumber, Checkbox, message, Spin, Row, Col, Divider, Descriptions } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UserOutlined, TeamOutlined, ThunderboltOutlined, EyeOutlined } from '@ant-design/icons';

const { Option } = Select;

const Character: React.FC = () => {
  const [form] = Form.useForm();
  const [batchForm] = Form.useForm();
  const [modalVisible, setModalVisible] = useState(false);
  const [batchModalVisible, setBatchModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [characters, setCharacters] = useState([]);
  const [worldViews, setWorldViews] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  // 固定的角色类型选项
  const roleTypes = [
    { value: '主角', label: '主角', description: '主角角色' },
    { value: '正义伙伴', label: '正义伙伴', description: '正义伙伴角色' },
    { value: '反派', label: '反派', description: '反派角色' },
    { value: '导师', label: '导师', description: '导师角色' },
    { value: '其他', label: '其他', description: '其他角色' },
    { value: '路人', label: '路人', description: '路人角色' }
  ];
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  
  // 监听批量生成表单的角色数量
  const characterCount = Form.useWatch('character_count', batchForm);

  // 监听编辑模态框的打开，设置表单值
  useEffect(() => {
    if (editModalVisible && selectedCharacter) {
      console.log('设置编辑表单值:', selectedCharacter);
      console.log('角色的worldview_id:', selectedCharacter.worldview_id);
      console.log('可用的世界观列表:', worldViews);
      console.log('匹配的世界观:', worldViews.find(w => w.worldview_id === selectedCharacter.worldview_id));
      
      // 检查worldview_id是否存在
      let worldviewId = selectedCharacter.worldview_id;
      if (!worldviewId) {
        console.warn('角色的worldview_id为空或未定义:', selectedCharacter);
        // 如果有可用的世界观，使用第一个作为默认值
        if (worldViews.length > 0) {
          worldviewId = worldViews[0].worldview_id;
          console.log('使用默认世界观:', worldViews[0]);
          message.info(`该角色没有关联的世界观，已自动选择: ${worldViews[0].name}`);
        } else {
          message.warning('该角色没有关联的世界观，且没有可用的世界观');
        }
      }
      
      form.setFieldsValue({
        worldview_id: worldviewId || undefined, // 如果为空则设置为undefined
        description: selectedCharacter.background || '',
        role_type: selectedCharacter.role_type,
        additional_requirements: ''
      });
      
      // 验证表单值是否设置成功
      setTimeout(() => {
        const formValues = form.getFieldsValue();
        console.log('表单实际值:', formValues);
      }, 100);
    }
  }, [editModalVisible, selectedCharacter, form, worldViews]);

  // 加载数据
  useEffect(() => {
    loadWorldViews();
    loadCharacters();
  }, []);

  const loadWorldViews = async () => {
    try {
      console.log('开始加载世界观...');
      const response = await fetch('http://localhost:8000/api/v1/world/simple-list');
      console.log('世界观API响应状态:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('世界观数据:', data);
      console.log('世界观数据结构:', data.worldviews);
      if (data.worldviews && data.worldviews.length > 0) {
        console.log('第一个世界观:', data.worldviews[0]);
        console.log('第一个世界观的ID:', data.worldviews[0].worldview_id);
      }
      setWorldViews(data.worldviews || []);
    } catch (error) {
      console.error('加载世界观失败:', error);
      message.error('加载世界观失败，请检查后端服务是否启动');
    }
  };

  const loadCharacters = async () => {
    try {
      console.log('开始加载角色...');
      const response = await fetch('http://localhost:8000/api/v1/character/list');
      console.log('角色API响应状态:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('角色数据:', data);
      // 调试：检查第一个角色的worldview_id
      if (data && data.length > 0) {
        console.log('第一个角色的worldview_id:', data[0].worldview_id);
        console.log('第一个角色完整数据:', data[0]);
      }
      setCharacters(data || []);
    } catch (error) {
      console.error('加载角色失败:', error);
      message.error('加载角色失败，请检查后端服务是否启动');
    }
  };


  const columns = [
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <UserOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: '角色类型',
      dataIndex: 'role_type',
      key: 'role_type',
      render: (type: string) => {
        const colorMap = {
          '主角': 'red',
          '正义伙伴': 'blue',
          '反派': 'purple',
          '导师': 'green',
          '其他': 'orange',
          '路人': 'default'
        };
        return <Tag color={colorMap[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '基本信息',
      key: 'basic_info',
      render: (_, record) => (
        <div>
          <div><strong>年龄：</strong>{record.age}岁</div>
          <div><strong>性别：</strong>{record.gender}</div>
          {record.metadata?.appearance && (
            <div><strong>外貌：</strong>{record.metadata.appearance}</div>
          )}
        </div>
      ),
    },
    {
      title: '性格',
      dataIndex: 'personality_traits',
      key: 'personality_traits',
      render: (traits: any[]) => (
        <Space wrap>
          {traits && traits.length > 0 ? (
            traits.map((trait, index) => {
              const traitText = typeof trait === 'string' ? trait : trait.trait;
              return <Tag key={index} color="purple">{traitText}</Tag>;
            })
          ) : (
            <span style={{ color: '#999' }}>暂无性格特质</span>
          )}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} onClick={() => handleViewCharacter(record)}>查看</Button>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEditCharacter(record)}>编辑</Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDeleteCharacter(record)}>删除</Button>
        </Space>
      ),
    },
  ];

  const handleCreateCharacter = async (values: any) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/character/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worldview_id: values.worldview_id,
          description: values.description,
          role_type: values.role_type,
          additional_requirements: values.additional_requirements
        }),
        signal: AbortSignal.timeout(600000), // 600秒超时
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '生成失败');
      }

      const character = await response.json();
      console.log('角色生成结果:', character);
      
      message.success('角色生成成功！');
      setModalVisible(false);
      form.resetFields();
      // 重新加载角色列表
      await loadCharacters();
    } catch (error: any) {
      console.error('创建角色失败:', error);
      message.error('创建角色失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchCreateCharacters = async (values: any) => {
    setBatchLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/character/batch-create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worldview_id: values.worldview_id,
          description: values.description,
          character_count: values.character_count,
          role_types: values.role_types,
          additional_requirements: values.additional_requirements
        }),
        signal: AbortSignal.timeout(600000), // 600秒超时
      });

      if (!response.ok) {
        throw new Error('批量生成失败');
      }

      const data = await response.json();
      if (data.success) {
        message.success(`成功生成${data.total_count}个角色！`);
        setBatchModalVisible(false);
        batchForm.resetFields();
        // 重新加载角色列表
        await loadCharacters();
      } else {
        message.error(data.message || '批量生成失败');
      }
    } catch (error) {
      message.error(`批量生成失败: ${error.message}`);
    } finally {
      setBatchLoading(false);
    }
  };

  // 查看角色详情
  const handleViewCharacter = (character: any) => {
    setSelectedCharacter(character);
    setViewModalVisible(true);
  };

  // 编辑角色
  const handleEditCharacter = (character: any) => {
    console.log('编辑角色数据:', character);
    console.log('角色的worldview_id:', character.worldview_id);
    setSelectedCharacter(character);
    setEditModalVisible(true);
  };

  // 删除角色
  const handleDeleteCharacter = (character: any) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除角色"${character.name}"吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          setLoading(true);
          const response = await fetch(`http://localhost:8000/api/v1/character/${character.id}`, {
            method: 'DELETE',
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '删除失败');
          }

          const result = await response.json();
          message.success(result.message || '角色删除成功！');
          await loadCharacters(); // 重新加载角色列表
        } catch (error: any) {
          console.error('删除角色失败:', error);
          message.error('删除角色失败: ' + error.message);
        } finally {
          setLoading(false);
        }
      },
    });
  };

  // 更新角色
  const handleUpdateCharacter = async (values: any) => {
    if (!selectedCharacter) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/character/${selectedCharacter.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worldview_id: values.worldview_id,
          description: values.description,
          role_type: values.role_type,
          additional_requirements: values.additional_requirements
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '更新失败');
      }

      message.success('角色更新成功！');
      setEditModalVisible(false);
      form.resetFields();
      await loadCharacters(); // 重新加载角色列表
    } catch (error: any) {
      console.error('更新角色失败:', error);
      message.error('更新角色失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card 
        title="角色管理" 
        extra={
          <Space>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setModalVisible(true)}
              loading={loading}
            >
              单个角色
            </Button>
            <Button 
              type="default" 
              icon={<TeamOutlined />}
              onClick={() => setBatchModalVisible(true)}
              loading={batchLoading}
            >
              批量生成
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={characters}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="创建单个角色"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
        confirmLoading={loading}
      >
        <Form form={form} onFinish={handleCreateCharacter} layout="vertical">
          <Form.Item
            name="worldview_id"
            label="选择世界观"
            rules={[{ required: true, message: '请选择世界观' }]}
          >
            <Select placeholder="请选择世界观" loading={worldViews.length === 0}>
              {worldViews.map((world: any) => (
                <Option key={world.worldview_id} value={world.worldview_id}>
                  {world.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="角色描述"
            rules={[{ required: true, message: '请输入角色描述' }]}
          >
            <Input.TextArea 
              rows={3} 
              placeholder="请用一句话描述你想要创建的角色，例如：一个年轻的修仙者，性格勇敢但有些冲动，来自小门派，梦想成为仙尊"
            />
          </Form.Item>

          <Form.Item
            name="role_type"
            label="角色类型"
            rules={[{ required: true, message: '请选择角色类型' }]}
          >
            <Select placeholder="请选择角色类型">
              {roleTypes.map((roleType: any) => (
                <Option key={roleType.value} value={roleType.value}>
                  {roleType.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="additional_requirements"
            label="额外要求（可选）"
          >
            <Input.TextArea 
              rows={2} 
              placeholder="可以添加额外的要求，例如：年龄范围、性别、特殊能力、外貌特征等"
            />
          </Form.Item>

          <Divider />
          
          <div style={{ textAlign: 'center', color: '#666' }}>
            <UserOutlined style={{ marginRight: 8 }} />
            系统将根据您的描述智能生成符合世界观的角色
          </div>
        </Form>
      </Modal>

      {/* 批量生成角色模态框 */}
      <Modal
        title="批量生成角色"
        open={batchModalVisible}
        onCancel={() => setBatchModalVisible(false)}
        onOk={() => batchForm.submit()}
        width={800}
        confirmLoading={batchLoading}
      >
        <Form form={batchForm} onFinish={handleBatchCreateCharacters} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="worldview_id"
                label="选择世界观"
                rules={[{ required: true, message: '请选择世界观' }]}
              >
                <Select placeholder="请选择世界观" loading={worldViews.length === 0}>
                  {worldViews.map((world: any) => (
                    <Option key={world.worldview_id} value={world.worldview_id}>
                      {world.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="character_count"
                label="角色数量"
                rules={[{ required: true, message: '请输入角色数量' }]}
              >
                <InputNumber 
                  min={1} 
                  max={20} 
                  placeholder="1-20个角色" 
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="角色描述"
            rules={[{ required: true, message: '请输入角色描述' }]}
          >
            <Input.TextArea 
              rows={3} 
              placeholder="请用一句话描述你想要生成的角色，例如：一群年轻的修仙者，他们来自不同的门派，有着不同的性格和背景"
            />
          </Form.Item>

          <Form.Item
            name="role_types"
            label="角色类型"
            rules={[{ required: true, message: '请选择至少一种角色类型' }]}
          >
            <Checkbox.Group>
              <Row>
                {roleTypes.map((roleType: any) => (
                  <Col span={8} key={roleType.value}>
                    <Checkbox value={roleType.value}>{roleType.label}</Checkbox>
                  </Col>
                ))}
              </Row>
            </Checkbox.Group>
          </Form.Item>

          <Form.Item
            name="additional_requirements"
            label="额外要求（可选）"
          >
            <Input.TextArea 
              rows={2} 
              placeholder="可以添加额外的要求，例如：年龄范围、性别比例、特殊能力等"
            />
          </Form.Item>

          <Divider />
          
          <div style={{ textAlign: 'center', color: '#666' }}>
            <ThunderboltOutlined style={{ marginRight: 8 }} />
            系统将根据您的描述和设置，智能生成{characterCount || '多个'}符合世界观的角色
          </div>
        </Form>
      </Modal>

      {/* 查看角色详情模态框 */}
      <Modal
        title="角色详情"
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>
        ]}
        width="90%"
        style={{ maxWidth: 1200 }}
        bodyStyle={{ maxHeight: '80vh', overflowY: 'auto' }}
        className="character-detail-modal"
      >
        {selectedCharacter && (
          <Descriptions 
            bordered 
            column={{ xs: 1, sm: 1, md: 2, lg: 2, xl: 2, xxl: 2 }}
            size="middle"
            labelStyle={{ 
              fontWeight: 'bold', 
              backgroundColor: '#fafafa',
              minWidth: '120px'
            }}
            contentStyle={{ 
              wordBreak: 'break-word',
              maxWidth: '400px'
            }}
          >
            <Descriptions.Item label="姓名" span={2}>
              <Space>
                <UserOutlined />
                <strong style={{ fontSize: '16px' }}>{selectedCharacter.name}</strong>
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="角色类型">
              <Tag color={
                selectedCharacter.role_type === '主角' ? 'red' :
                selectedCharacter.role_type === '正义伙伴' ? 'blue' :
                selectedCharacter.role_type === '反派' ? 'purple' :
                selectedCharacter.role_type === '导师' ? 'green' :
                selectedCharacter.role_type === '其他' ? 'orange' : 'default'
              }>
                {selectedCharacter.role_type}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="年龄">
              {selectedCharacter.age}岁
            </Descriptions.Item>
            <Descriptions.Item label="性别">
              {selectedCharacter.gender}
            </Descriptions.Item>
            <Descriptions.Item label="外貌">
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '100px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {selectedCharacter.metadata?.appearance || '暂无外貌描述'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="背景" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '120px', 
                overflowY: 'auto',
                padding: '4px 0',
                lineHeight: '1.6'
              }}>
                {selectedCharacter.background || '暂无背景信息'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="性格特质" span={2}>
              <Space wrap>
                {selectedCharacter.personality_traits && selectedCharacter.personality_traits.length > 0 ? (
                  selectedCharacter.personality_traits.map((trait: any, index: number) => {
                    const traitText = typeof trait === 'string' ? trait : trait.trait;
                    return <Tag key={index} color="purple">{traitText}</Tag>;
                  })
                ) : (
                  <span style={{ color: '#999' }}>暂无性格特质</span>
                )}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="目标" span={2}>
              <Space wrap>
                {selectedCharacter.goals && selectedCharacter.goals.length > 0 ? (
                  selectedCharacter.goals.map((goal: any, index: number) => (
                    <Tag key={index} color="cyan">
                      {typeof goal === 'string' ? goal : `${goal.goal} (${goal.type})`}
                    </Tag>
                  ))
                ) : (
                  <span style={{ color: '#999' }}>暂无目标</span>
                )}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="技能" span={2}>
              <Space wrap>
                {selectedCharacter.techniques && selectedCharacter.techniques.length > 0 ? (
                  selectedCharacter.techniques.map((tech: any, index: number) => (
                    <Tag key={index} color="orange">
                      {typeof tech === 'string' ? tech : `${tech.name} (${tech.level})`}
                    </Tag>
                  ))
                ) : (
                  <span style={{ color: '#999' }}>暂无技能</span>
                )}
              </Space>
            </Descriptions.Item>
            <Descriptions.Item label="成长潜力" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '80px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {selectedCharacter.resources?.growth_potential || '暂无信息'}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="关系" span={2}>
              <div className="character-detail-scrollable" style={{ 
                maxHeight: '120px', 
                overflowY: 'auto',
                padding: '4px 0'
              }}>
                {selectedCharacter.relationships ? (
                  <div>
                    {selectedCharacter.relationships.family && (
                      <div style={{ marginBottom: '8px' }}>
                        <strong>家庭：</strong>{selectedCharacter.relationships.family}
                      </div>
                    )}
                    {selectedCharacter.relationships.master && (
                      <div style={{ marginBottom: '8px' }}>
                        <strong>师父：</strong>{selectedCharacter.relationships.master}
                      </div>
                    )}
                    {selectedCharacter.relationships.friends && selectedCharacter.relationships.friends.length > 0 && (
                      <div style={{ marginBottom: '8px' }}>
                        <strong>朋友：</strong>{selectedCharacter.relationships.friends.join(', ')}
                      </div>
                    )}
                    {selectedCharacter.relationships.enemies && selectedCharacter.relationships.enemies.length > 0 && (
                      <div style={{ marginBottom: '8px' }}>
                        <strong>敌人：</strong>{selectedCharacter.relationships.enemies.join(', ')}
                      </div>
                    )}
                  </div>
                ) : (
                  <span style={{ color: '#999' }}>暂无关系信息</span>
                )}
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {new Date(selectedCharacter.created_at).toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={selectedCharacter.status === 'active' ? 'green' : 'red'}>
                {selectedCharacter.status === 'active' ? '活跃' : '非活跃'}
              </Tag>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* 编辑角色模态框 */}
      <Modal
        title="编辑角色"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
        confirmLoading={loading}
      >
        <Form form={form} onFinish={handleUpdateCharacter} layout="vertical">
          <Form.Item
            name="worldview_id"
            label="世界观"
            rules={[{ required: true, message: '请选择世界观' }]}
          >
            <Select placeholder="请选择世界观">
              {worldViews.map((world: any) => (
                <Option key={world.worldview_id} value={world.worldview_id}>
                  {world.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="角色描述"
            rules={[{ required: true, message: '请输入角色描述' }]}
          >
            <Input.TextArea 
              rows={4} 
              placeholder="请描述角色的基本信息，例如：一个年轻的剑客，擅长快剑，性格孤傲"
            />
          </Form.Item>

          <Form.Item
            name="role_type"
            label="角色类型"
            rules={[{ required: true, message: '请选择角色类型' }]}
          >
            <Select placeholder="请选择角色类型">
              {roleTypes.map(role => (
                <Option key={role.value} value={role.value}>
                  {role.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="additional_requirements"
            label="额外要求（可选）"
          >
            <Input.TextArea 
              rows={2} 
              placeholder="可以添加额外的要求，例如：年龄范围、性别、特殊能力、外貌特征等"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Character;
