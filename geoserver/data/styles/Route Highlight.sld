<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0" 
  xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
  xmlns="http://www.opengis.net/sld" 
  xmlns:ogc="http://www.opengis.net/ogc" 
  xmlns:xlink="http://www.w3.org/1999/xlink" 
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<NamedLayer>
<Name>GTFS Route Highlight</Name>
<UserStyle>
  <Name>Route Highlight</Name>
  <Title>Route Highlight</Title>
  <Abstract>Colors the GTFS route lines a single color</Abstract>
  <OverlapBehavior>EARLIEST_ON_TOP</OverlapBehavior>
    <FeatureTypeStyle>
      <!-- 
         Draw the Highlight Line
       -->
      <Rule>
        <LineSymbolizer>
          <Stroke>
            <CssParameter name="stroke">#f54c00</CssParameter>
            <CssParameter name="stroke-linejoin">round</CssParameter>
            <CssParameter name="stroke-width">2.0</CssParameter>
            <CssParameter name="stroke-opacity">1.0</CssParameter>
          </Stroke>
        </LineSymbolizer>
      </Rule>

      <!-- 
         BUS STYLE
       -->
      <Rule>
        <ogc:Filter>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>route_type</ogc:PropertyName>
                <ogc:Literal>3</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        <TextSymbolizer>
            <Label><ogc:PropertyName>route_id</ogc:PropertyName></Label>
            <Font>
                <CssParameter name="font-family"><ogc:Literal>Lucida Sans</ogc:Literal></CssParameter>
                <CssParameter name="font-size"><ogc:Literal>9.0</ogc:Literal></CssParameter>
                <CssParameter name="font-style"><ogc:Literal>normal</ogc:Literal></CssParameter>
                <CssParameter name="font-weight"><ogc:Literal>bold</ogc:Literal></CssParameter>
            </Font>
            <LabelPlacement>
                <PointPlacement>
                    <AnchorPoint>
                        <AnchorPointX><ogc:Literal>0.0</ogc:Literal></AnchorPointX>
                        <AnchorPointY><ogc:Literal>0.0</ogc:Literal></AnchorPointY>
                    </AnchorPoint>
                    <Displacement>
                        <DisplacementX><ogc:Literal>-5.0</ogc:Literal></DisplacementX>
                        <DisplacementY><ogc:Literal>-5.0</ogc:Literal></DisplacementY>
                    </Displacement>
                    <Rotation><ogc:Literal>0.0</ogc:Literal></Rotation>
                </PointPlacement>
            </LabelPlacement>
            <Fill>
                <CssParameter name="fill">#FFFFFF</CssParameter>
                <CssParameter name="fill-opacity">1.0</CssParameter>
            </Fill>
            <Graphic>
               <Mark>
                   <WellKnownName>circle</WellKnownName>
                   <Fill>
                     <CssParameter name="fill">#f54c00</CssParameter>
                     <CssParameter name="fill-opacity">1.0</CssParameter>
                   </Fill>
               </Mark>
               <Size><ogc:Literal>16.0</ogc:Literal></Size>
            </Graphic>
            <!-- 
                 maxDisplacement: will search for another location within maxDisplacement pixels from the pre-computed label point
                 repeat:  should always be a larger number than the value for maxDisplacement 
                 spaceAround:   w/negative value allows overlaping lables of x pixels
                 labelAllGroup: option makes sure that all of the segments in a line group are labeled instead of just the longest one
                 see: http://geoserver.org/display/GEOSDOC/LabelingOptions
              -->
            <VendorOption name="spaceAround">50</VendorOption>
            <VendorOption name="group">true</VendorOption>
            <VendorOption name="labelAllGroup">true</VendorOption>
            <VendorOption name="minGroupDistance">200</VendorOption>
            <VendorOption name="maxDisplacement">350</VendorOption>
            <VendorOption name="repeat">400</VendorOption>
        </TextSymbolizer>
      </Rule>

      <!-- 
         Light Rail STYLE
       -->
      <Rule>
        <ogc:Filter>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>route_type</ogc:PropertyName>
                <ogc:Literal>0</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        <TextSymbolizer>
            <Label>Light Rail</Label>
            <Font>
                <CssParameter name="font-family"><ogc:Literal>Lucida Sans</ogc:Literal></CssParameter>
                <CssParameter name="font-size"><ogc:Literal>9.0</ogc:Literal></CssParameter>
                <CssParameter name="font-style"><ogc:Literal>normal</ogc:Literal></CssParameter>
                <CssParameter name="font-weight"><ogc:Literal>bold</ogc:Literal></CssParameter>
            </Font>
            <LabelPlacement>
                <PointPlacement>
                    <AnchorPoint>
                        <AnchorPointX><ogc:Literal>0.0</ogc:Literal></AnchorPointX>
                        <AnchorPointY><ogc:Literal>0.0</ogc:Literal></AnchorPointY>
                    </AnchorPoint>
                    <Displacement>
                        <DisplacementX><ogc:Literal>-5.0</ogc:Literal></DisplacementX>
                        <DisplacementY><ogc:Literal>-5.0</ogc:Literal></DisplacementY>
                    </Displacement>
                    <Rotation><ogc:Literal>0.0</ogc:Literal></Rotation>
                </PointPlacement>
            </LabelPlacement>
            <Fill>
                <CssParameter name="fill">#FFFFFF</CssParameter>
                <CssParameter name="fill-opacity">1.0</CssParameter>
            </Fill>
            <Graphic>
               <Mark>
                   <WellKnownName>rectangle</WellKnownName>
                   <Fill>
                     <CssParameter name="fill">#f54c00</CssParameter>
                     <CssParameter name="fill-opacity">1.0</CssParameter>
                   </Fill>
               </Mark>
               <Size><ogc:Literal>16.0</ogc:Literal></Size>
            </Graphic>
            <!-- 
                 maxDisplacement: will search for another location within maxDisplacement pixels from the pre-computed label point
                 repeat:  should always be a larger number than the value for maxDisplacement 
                 spaceAround:   w/negative value allows overlaping lables of x pixels
                 labelAllGroup: option makes sure that all of the segments in a line group are labeled instead of just the longest one
                 see: http://geoserver.org/display/GEOSDOC/LabelingOptions
              -->
            <VendorOption name="spaceAround">50</VendorOption>
            <VendorOption name="group">true</VendorOption>
            <VendorOption name="labelAllGroup">true</VendorOption>
            <VendorOption name="minGroupDistance">200</VendorOption>
            <VendorOption name="maxDisplacement">350</VendorOption>
            <VendorOption name="repeat">400</VendorOption>
        </TextSymbolizer>
      </Rule>

      <!-- 
          Heavy Rail STYLE
       -->
      <Rule>
        <ogc:Filter>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>route_type</ogc:PropertyName>
                <ogc:Literal>2</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        <TextSymbolizer>
            <Label>Heavy Rail</Label>
            <Font>
                <CssParameter name="font-family"><ogc:Literal>Lucida Sans</ogc:Literal></CssParameter>
                <CssParameter name="font-size"><ogc:Literal>9.0</ogc:Literal></CssParameter>
                <CssParameter name="font-style"><ogc:Literal>normal</ogc:Literal></CssParameter>
                <CssParameter name="font-weight"><ogc:Literal>bold</ogc:Literal></CssParameter>
            </Font>
            <LabelPlacement>
                <PointPlacement>
                    <AnchorPoint>
                        <AnchorPointX><ogc:Literal>0.0</ogc:Literal></AnchorPointX>
                        <AnchorPointY><ogc:Literal>0.0</ogc:Literal></AnchorPointY>
                    </AnchorPoint>
                    <Displacement>
                        <DisplacementX><ogc:Literal>-5.0</ogc:Literal></DisplacementX>
                        <DisplacementY><ogc:Literal>-5.0</ogc:Literal></DisplacementY>
                    </Displacement>
                    <Rotation><ogc:Literal>0.0</ogc:Literal></Rotation>
                </PointPlacement>
            </LabelPlacement>
            <Fill>
                <CssParameter name="fill">#FFFFFF</CssParameter>
                <CssParameter name="fill-opacity">1.0</CssParameter>
            </Fill>
            <Graphic>
               <Mark>
                   <WellKnownName>rectangle</WellKnownName>
                   <Fill>
                     <CssParameter name="fill">#f54c00</CssParameter>
                     <CssParameter name="fill-opacity">1.0</CssParameter>
                   </Fill>
               </Mark>
               <Size><ogc:Literal>16.0</ogc:Literal></Size>
            </Graphic>
            <!-- 
                 maxDisplacement: will search for another location within maxDisplacement pixels from the pre-computed label point
                 repeat:  should always be a larger number than the value for maxDisplacement 
                 spaceAround:   w/negative value allows overlaping lables of x pixels
                 labelAllGroup: option makes sure that all of the segments in a line group are labeled instead of just the longest one
                 see: http://geoserver.org/display/GEOSDOC/LabelingOptions
              -->
            <VendorOption name="spaceAround">50</VendorOption>
            <VendorOption name="group">true</VendorOption>
            <VendorOption name="labelAllGroup">true</VendorOption>
            <VendorOption name="minGroupDistance">200</VendorOption>
            <VendorOption name="maxDisplacement">350</VendorOption>
            <VendorOption name="repeat">400</VendorOption>
        </TextSymbolizer>
      </Rule>        
    </FeatureTypeStyle>
  </UserStyle>
</NamedLayer>
</StyledLayerDescriptor>