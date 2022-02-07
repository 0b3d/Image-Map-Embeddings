<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyLocal="1" simplifyDrawingHints="0" simplifyMaxScale="1" styleCategories="AllStyleCategories" readOnly="0" labelsEnabled="0" simplifyAlgorithm="0" hasScaleBasedVisibilityFlag="0" minScale="2500" version="3.16.2-Hannover" maxScale="2500" simplifyDrawingTol="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal endField="" durationUnit="min" endExpression="" fixedDuration="0" enabled="0" accumulate="0" durationField="" mode="0" startExpression="" startField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="RuleRenderer" symbollevels="0" forceraster="0" enableorderby="0">
    <rules key="{dac8152b-a820-4b10-8542-2aee33313c70}">
      <rule label="All other values" checkstate="0" symbol="0" filter="(DescriptiveTerm IS NOT 'Triangulation Point Or Pillar') AND&#xa;(DescriptiveTerm IS NOT 'Spot Height') AND&#xa;(DescriptiveTerm IS NOT 'Structure') AND&#xa;(DescriptiveGroup IS NOT 'Historic Interest') AND&#xa;(DescriptiveGroup IS NOT 'Structure') AND&#xa;(DescriptiveGroup IS NOT 'Inland Water') AND&#xa;(DescriptiveTerm IS NOT 'Positioned Nonconiferous Tree') AND&#xa;(DescriptiveTerm IS NOT 'Positioned Coniferous Tree')" key="{e3918dc6-6edb-41a8-b6df-02997eb5f492}"/>
      <rule label="Triangulation Point or Pillar" checkstate="0" symbol="1" filter="DescriptiveTerm = 'Triangulation Point Or Pillar'" key="{b8a82d34-940a-4472-adeb-8f5afcf508f4}"/>
      <rule label="Historic Sites" checkstate="0" symbol="2" filter="DescriptiveGroup = 'Historic Interest'" key="{9ea7e554-023a-40b4-8a43-361ee367d60c}"/>
      <rule label="Spot Height" checkstate="0" symbol="3" filter="DescriptiveTerm = 'Spot Height'" key="{8c520da2-529e-4fee-acfa-7889d772a9cf}"/>
      <rule label="Structures" checkstate="0" symbol="4" filter="DescriptiveTerm = 'Structure' OR DescriptiveGroup = 'Structure'" key="{4aa33588-465d-46f3-8dce-af12099cdb34}"/>
      <rule label="Inland Water" checkstate="0" symbol="5" filter="DescriptiveGroup = 'Inland Water'" key="{59c18d4e-45c0-4d2a-b329-a3a960931152}"/>
      <rule label="Positioned Nonconiferous Tree" symbol="6" filter="DescriptiveTerm = 'Positioned Nonconiferous Tree'" key="{200d9675-cfc4-4f40-86fd-1c5b39b384bf}"/>
      <rule label="Positioned Coniferous Tree" symbol="7" filter="DescriptiveTerm = 'Positioned Coniferous Tree'" key="{fee720b0-dd96-4aa8-927d-2ff6579d33b1}"/>
    </rules>
    <symbols>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="0" force_rhr="0">
        <layer class="SimpleMarker" pass="1" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,0,0,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="1" force_rhr="0">
        <layer class="SimpleMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="255,255,255,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,-0.20000000000000001" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.2" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="2.6" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="0,0,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="0.5" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="2" force_rhr="0">
        <layer class="SimpleMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="208,104,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="star" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="208,104,0,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="3" force_rhr="0">
        <layer class="SimpleMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="cross" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.25" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="2" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="4" force_rhr="0">
        <layer class="SimpleMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="0,0,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="1" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="5" force_rhr="0">
        <layer class="SimpleMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="0,199,255,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="circle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="no" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="1" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="6" force_rhr="0">
        <layer class="SvgMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="0,85,0,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="symbol/landuse_deciduous.svg" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="5" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="marker" clip_to_extent="1" name="7" force_rhr="0">
        <layer class="SvgMarker" pass="0" enabled="1" locked="0">
          <prop v="0" k="angle"/>
          <prop v="0,85,0,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="symbol/landuse_coniferous.svg" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="5" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" type="QString" name="name"/>
              <Option name="properties"/>
              <Option value="collection" type="QString" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory scaleBasedVisibility="0" spacingUnit="MM" minimumSize="0" width="15" direction="0" backgroundColor="#ffffff" rotationOffset="270" backgroundAlpha="255" maxScaleDenominator="1e+08" showAxis="1" height="15" opacity="1" penColor="#000000" spacing="5" sizeType="MM" scaleDependency="Area" barWidth="5" lineSizeType="MM" lineSizeScale="3x:0,0,0,0,0,0" sizeScale="3x:0,0,0,0,0,0" minScaleDenominator="0" enabled="0" penWidth="0" spacingUnitScale="3x:0,0,0,0,0,0" penAlpha="255" diagramOrientation="Up" labelPlacementMethod="XHeight">
      <fontProperties style="" description="Sans Serif,9,-1,5,50,0,0,0,0,0"/>
      <attribute color="#000000" label="" field=""/>
      <axisSymbol>
        <symbol alpha="1" type="line" clip_to_extent="1" name="" force_rhr="0">
          <layer class="SimpleLine" pass="0" enabled="1" locked="0">
            <prop v="0" k="align_dash_pattern"/>
            <prop v="square" k="capstyle"/>
            <prop v="5;2" k="customdash"/>
            <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
            <prop v="MM" k="customdash_unit"/>
            <prop v="0" k="dash_pattern_offset"/>
            <prop v="3x:0,0,0,0,0,0" k="dash_pattern_offset_map_unit_scale"/>
            <prop v="MM" k="dash_pattern_offset_unit"/>
            <prop v="0" k="draw_inside_polygon"/>
            <prop v="bevel" k="joinstyle"/>
            <prop v="35,35,35,255" k="line_color"/>
            <prop v="solid" k="line_style"/>
            <prop v="0.26" k="line_width"/>
            <prop v="MM" k="line_width_unit"/>
            <prop v="0" k="offset"/>
            <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
            <prop v="MM" k="offset_unit"/>
            <prop v="0" k="ring_filter"/>
            <prop v="0" k="tweak_dash_pattern_on_corners"/>
            <prop v="0" k="use_custom_dash"/>
            <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" type="QString" name="name"/>
                <Option name="properties"/>
                <Option value="collection" type="QString" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="0" obstacle="0" priority="0" showAll="1" zIndex="0" dist="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option value="" type="QString" name="name"/>
        <Option name="properties"/>
        <Option value="collection" type="QString" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="OBJECTID" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="TOID" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="FeatureCode" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="Version" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="VersionDate" configurationFlags="None">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="Theme" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="AccuracyOfPosition" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="Make" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DescriptiveGroup" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="DescriptiveTerm" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="PhysicalLevel" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="HeightAboveDatum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="AccuracyOfHeightAboveDatum" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="OBJECTID"/>
    <alias index="1" name="" field="TOID"/>
    <alias index="2" name="" field="FeatureCode"/>
    <alias index="3" name="" field="Version"/>
    <alias index="4" name="" field="VersionDate"/>
    <alias index="5" name="" field="Theme"/>
    <alias index="6" name="" field="AccuracyOfPosition"/>
    <alias index="7" name="" field="Make"/>
    <alias index="8" name="" field="DescriptiveGroup"/>
    <alias index="9" name="" field="DescriptiveTerm"/>
    <alias index="10" name="" field="PhysicalLevel"/>
    <alias index="11" name="" field="HeightAboveDatum"/>
    <alias index="12" name="" field="AccuracyOfHeightAboveDatum"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="OBJECTID" expression=""/>
    <default applyOnUpdate="0" field="TOID" expression=""/>
    <default applyOnUpdate="0" field="FeatureCode" expression=""/>
    <default applyOnUpdate="0" field="Version" expression=""/>
    <default applyOnUpdate="0" field="VersionDate" expression=""/>
    <default applyOnUpdate="0" field="Theme" expression=""/>
    <default applyOnUpdate="0" field="AccuracyOfPosition" expression=""/>
    <default applyOnUpdate="0" field="Make" expression=""/>
    <default applyOnUpdate="0" field="DescriptiveGroup" expression=""/>
    <default applyOnUpdate="0" field="DescriptiveTerm" expression=""/>
    <default applyOnUpdate="0" field="PhysicalLevel" expression=""/>
    <default applyOnUpdate="0" field="HeightAboveDatum" expression=""/>
    <default applyOnUpdate="0" field="AccuracyOfHeightAboveDatum" expression=""/>
  </defaults>
  <constraints>
    <constraint unique_strength="1" notnull_strength="1" field="OBJECTID" exp_strength="0" constraints="3"/>
    <constraint unique_strength="0" notnull_strength="0" field="TOID" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="FeatureCode" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="Version" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="VersionDate" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="Theme" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="AccuracyOfPosition" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="Make" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="DescriptiveGroup" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="DescriptiveTerm" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="PhysicalLevel" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="HeightAboveDatum" exp_strength="0" constraints="0"/>
    <constraint unique_strength="0" notnull_strength="0" field="AccuracyOfHeightAboveDatum" exp_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="OBJECTID"/>
    <constraint desc="" exp="" field="TOID"/>
    <constraint desc="" exp="" field="FeatureCode"/>
    <constraint desc="" exp="" field="Version"/>
    <constraint desc="" exp="" field="VersionDate"/>
    <constraint desc="" exp="" field="Theme"/>
    <constraint desc="" exp="" field="AccuracyOfPosition"/>
    <constraint desc="" exp="" field="Make"/>
    <constraint desc="" exp="" field="DescriptiveGroup"/>
    <constraint desc="" exp="" field="DescriptiveTerm"/>
    <constraint desc="" exp="" field="PhysicalLevel"/>
    <constraint desc="" exp="" field="HeightAboveDatum"/>
    <constraint desc="" exp="" field="AccuracyOfHeightAboveDatum"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="">
    <columns>
      <column hidden="0" width="-1" type="field" name="OBJECTID"/>
      <column hidden="0" width="-1" type="field" name="TOID"/>
      <column hidden="0" width="-1" type="field" name="FeatureCode"/>
      <column hidden="0" width="-1" type="field" name="Version"/>
      <column hidden="0" width="-1" type="field" name="VersionDate"/>
      <column hidden="0" width="-1" type="field" name="Theme"/>
      <column hidden="0" width="-1" type="field" name="AccuracyOfPosition"/>
      <column hidden="0" width="-1" type="field" name="Make"/>
      <column hidden="0" width="-1" type="field" name="DescriptiveGroup"/>
      <column hidden="0" width="-1" type="field" name="DescriptiveTerm"/>
      <column hidden="0" width="-1" type="field" name="PhysicalLevel"/>
      <column hidden="0" width="-1" type="field" name="HeightAboveDatum"/>
      <column hidden="0" width="-1" type="field" name="AccuracyOfHeightAboveDatum"/>
      <column hidden="1" width="-1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="AccuracyOfHeightAboveDatum" editable="1"/>
    <field name="AccuracyOfPosition" editable="1"/>
    <field name="DescriptiveGroup" editable="1"/>
    <field name="DescriptiveTerm" editable="1"/>
    <field name="FeatureCode" editable="1"/>
    <field name="HeightAboveDatum" editable="1"/>
    <field name="Make" editable="1"/>
    <field name="OBJECTID" editable="1"/>
    <field name="PhysicalLevel" editable="1"/>
    <field name="TOID" editable="1"/>
    <field name="Theme" editable="1"/>
    <field name="Version" editable="1"/>
    <field name="VersionDate" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="AccuracyOfHeightAboveDatum" labelOnTop="0"/>
    <field name="AccuracyOfPosition" labelOnTop="0"/>
    <field name="DescriptiveGroup" labelOnTop="0"/>
    <field name="DescriptiveTerm" labelOnTop="0"/>
    <field name="FeatureCode" labelOnTop="0"/>
    <field name="HeightAboveDatum" labelOnTop="0"/>
    <field name="Make" labelOnTop="0"/>
    <field name="OBJECTID" labelOnTop="0"/>
    <field name="PhysicalLevel" labelOnTop="0"/>
    <field name="TOID" labelOnTop="0"/>
    <field name="Theme" labelOnTop="0"/>
    <field name="Version" labelOnTop="0"/>
    <field name="VersionDate" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>DescriptiveGroup</previewExpression>
  <mapTip>OS_ID</mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
