<?php

//#include <simgear/math/SGMath.hxx>

//void euler_get(float lat, float lon, float ox, float oy, float oz,
 //   float *head, float *pitch, float *roll)
//{

function euler_get($lat, $lon, $ox, $oy, $oz){
    /* FGMultiplayMgr::ProcessPosMsg */

   // SGVec3f angleAxis;
    //angleAxis(0) = ox;
    //angleAxis(1) = oy;
    //angleAxis(2) = oz;
	$angleAxis = array($ox, $oy, $ox);

    //SGQuatf ecOrient;
    //ecOrient = SGQuatf::fromAngleAxis(angleAxis);
	/// Create a quaternion from the angle axis representation where the angle
	/// is stored in the axis' length
	/*
	static SGQuat fromAngleAxis(const SGVec3<T>& axis)
	{
		T nAxis = norm(axis);
		if (nAxis <= SGLimits<T>::min())
		return SGQuat::unit();
		T angle2 = T(0.5)*nAxis;
		return fromRealImag(cos(angle2), T(sin(angle2)/nAxis)*axis);
	}
	*/
	function fromAngleAxis($axis){
		$nAxis = norm($axis);
	}


	/// The euclidean norm of the vector, that is what most people call length
	/* 
	template<typename T>
	inline
	T
	norm(const SGQuat<T>& v)
	{ return sqrt(dot(v, v)); }
	*/
	function norm($v){
		return sqrt( dot($v, $v) );
	}

	/// Scalar dot product
	/* template<typename T>
	inline
	T
	dot(const SGQuat<T>& v1, const SGQuat<T>& v2)
	{ return v1(0)*v2(0) + v1(1)*v2(1) + v1(2)*v2(2) + v1(3)*v2(3); }
	*/
	function dot($v1, $v2){
		return $v1[0] * $v2[0] + $v1[1] * $v2[1] + $v1[2] * $v2[2]; //+ $v1[3] * $v2[3]
	}



    /* FGAIMultiplayer::update */

    float lat_rad, lon_rad;
    lat_rad = lat * SGD_DEGREES_TO_RADIANS;
    lon_rad = lon * SGD_DEGREES_TO_RADIANS;

    SGQuatf qEc2Hl = SGQuatf::fromLonLatRad(lon_rad, lat_rad);

    SGQuatf hlOr = conj(qEc2Hl) * ecOrient;

    float hDeg, pDeg, rDeg;
    hlOr.getEulerDeg(hDeg, pDeg, rDeg);

    if(head)
        *head = hDeg;
    if(pitch)
        *pitch = pDeg;
    if(roll)
        *roll = rDeg;
}

